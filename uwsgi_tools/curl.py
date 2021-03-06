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
# end def


def curl(uwsgi_addr, method='GET', url=None, body=None, timeout=0, headers=()):
    parts_uwsgi, s = create_socket(uwsgi_addr, timeout=timeout)
    parts_url = urlsplit(url)
    host = parts_url.hostname or '127.0.0.1'
    uri = parts_url.path + "?" + parts_url.query + "#" + parts_url.fragment
    var = {
        # https://www.python.org/dev/peps/pep-3333/#environ-variables
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'REQUEST_METHOD': method,
        'PATH_INFO': parts_url.path,
        'REQUEST_URI': uri,
        'QUERY_STRING': parts_url.query,
        'SERVER_NAME':  host,
        'SERVER_PORT': parts_url.port or '',
        'HTTP_HOST': host,
    }
    # add the headers
    if not headers:  # make sure they exist.
        headers = []
    # end if
    for header in headers:
        key, value = header.split(":", maxsplit=1)
        key = 'HTTP_' + key.strip()
        value = value.strip()
        var[key] = value
    # end for
    result = ask_uwsgi(s, var, body)  # execute the actual request.
    s.close()
    return result
# end def


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

    parser.add_argument('-t', '--timeout', default=0.0, type=float,
                        help='Socket timeout')

    parser.add_argument('-H', '--header', action='append', dest='headers',
                        help='Add request header.\n'
                             'This option can be used multiple times to add/replace/remove multiple headers.')

    args = parser.parse_args(args or sys.argv[1:])
    http, success = run(args.uwsgi_addr[0], args.method, args.url, timeout=args.timeout, headers=args.headers)
    print(http)
    return 0 if success else 1
# end def


def run(uwsgi_addr, method='GET', url=None, body=None, timeout=0, headers=()):
    result = curl(uwsgi_addr, method, url, body, timeout, headers)
    response = parse_http_response(result)
    success = 200 <= response.status <= 299
    return result, success
# end def


if __name__ == '__main__':
    import sys
    res = cli(*sys.argv[1:])
    sys.exit(cli)
# end if
