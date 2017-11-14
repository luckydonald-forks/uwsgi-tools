import socket
from .utils import pack_uwsgi_vars
from .url_socket import create_socket, urlsplit


def ask_uwsgi(s, var, body=''):
    s.send(pack_uwsgi_vars(var) + body.encode('utf8'))
    response = []
    while 1:
        data = s.recv(4096)
        if not data:
            break
        response.append(data)
    return b''.join(response).decode('utf8')


def curl(uwsgi_addr, method='GET', url=None, body=None):
    parts_uwsgi, s = create_socket(uwsgi_addr)
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

    args = parser.parse_args(args or sys.argv[1:])
    print(curl(args.uwsgi_addr[0], args.method, args.url))


if __name__ == '__main__':
    import sys
    cli(*sys.argv[1:])
