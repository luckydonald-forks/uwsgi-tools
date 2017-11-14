import socket
from .utils import pack_uwsgi_vars, parse_addr, get_host_from_url
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


def curl(uwsgi_addr, method='GET', url=None):
    parts, s = create_socket(uwsgi_addr)
    parts2 = urlsplit(url)
    # end if
    uri = parts2.path + "?" + parts2.query + "#" + parts2.fragment
    var = {
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'REQUEST_METHOD': method,
        'PATH_INFO': parts2.path,
        'REQUEST_URI': uri,
        'QUERY_STRING': parts2.query,
        'SERVER_NAME': parts2.host or '127.0.0.1',
        'HTTP_HOST': parts2.host,
    }
    result = ask_uwsgi(s, var)
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
    cli()
