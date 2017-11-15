import socket
from .utils import pack_uwsgi_vars
from .url_socket import create_socket, urlsplit, parse_http_response


def ask_uwsgi(s, var, body=''):
    body = '' if body is None else body
    s.send(pack_uwsgi_vars(var) + body.encode('utf8'))
    response = []
    while 1:
        data = s.recv(4096)
        if not data:
            break
        response.append(data)
    return b''.join(response).decode('utf8')


def curl(uwsgi_addr, method='GET', url=None, body=None, timeout=0):
    parts_uwsgi, s = create_socket(uwsgi_addr, timeout=timeout)
    parts_url = urlsplit(url)
    host = parts_url.hostname or '127.0.0.1'
    uri = parts_url.path + "?" + parts_url.query + "#" + parts_url.fragment
    var = {
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'REQUEST_METHOD': method,
        'PATH_INFO': parts_url.path,
        'REQUEST_URI': uri,
        'QUERY_STRING': parts_url.query,
        'SERVER_NAME':  host,
        'HTTP_HOST': host,
    }
    result = ask_uwsgi(s, var, body)
    s.close()
    return result


def cli(*args):
    import argparse
    import sys

    parser = argparse.ArgumentParser()

    parser.add_argument('uwsgi_addr', nargs=1,
                        help='Remote address of uWSGI server')

    parser.add_argument('method', nargs='?', default='GET',
                        help='Request method')

    parser.add_argument('url', nargs='?', default='/',
                        help='Request URI optionally containing hostname')

    parser.add_argument('-t', '--timeout', nargs=1, default=0, type=float,
                        help='Socket timeout')

    args = parser.parse_args(args or sys.argv[1:])
    http, success = run(args.uwsgi_addr[0], args.method, args.url, timeout=args.timeout)
    print(http)
    return 0 if success else 4
# end def


def run(uwsgi_addr, method='GET', url=None, body=None, timeout=0):
    result = curl(uwsgi_addr, method, url, body, timeout)
    response = parse_http_response(result)
    success = 200 <= response.status <= 299
    return result, success
# end def

if __name__ == '__main__':
    import sys
    res = cli(*sys.argv[1:])
    sys.exit(cli)
