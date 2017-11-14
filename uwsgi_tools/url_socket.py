import socket
import sys
if sys.version_info[0] == 3:
    from urllib.parse import urlsplit
else:  # py 2
    from urlparse import urlsplit
# end if

NETWORK_SOCKET_TYPES_BY_SCHEME = {
    'tcp': socket.SOCK_STREAM,
    'udp': socket.SOCK_DGRAM,
}
FILE_SOCKET_TYPES_BY_SCHEME = {
    'unix':     socket.SOCK_STREAM,
    'unix+tcp': socket.SOCK_STREAM,
    'tcp+unix': socket.SOCK_STREAM,
    'unix+udp': socket.SOCK_DGRAM,
    'udp+unix': socket.SOCK_DGRAM,
}


class SocketInfos(object):
    def __init__(self, parts, params, address):
        super().__init__()
        self.params = params
        self.parts = parts
        self.address = address
    # end def
# end class


def create_socket_params(url):
    parts = urlsplit(url)
    if parts.scheme in FILE_SOCKET_TYPES_BY_SCHEME:
        socket_type = FILE_SOCKET_TYPES_BY_SCHEME[parts.scheme]
        connect = parts.netloc + parts.path
        parts.path = connect
        parts.hostname = '127.0.0.1'
        parts.port = ''
        return SocketInfos(parts, [(socket.AF_UNIX, socket_type)], connect)
    elif parts.scheme in NETWORK_SOCKET_TYPES_BY_SCHEME:
        socket_type = NETWORK_SOCKET_TYPES_BY_SCHEME[parts.scheme]
        # get a list with only the right socket types via socket.getaddrinfo()
        connect = (parts.hostname, parts.port)
        socket_configs = SocketInfos(
            parts,
            [conf for conf in socket.getaddrinfo(parts.hostname, parts.port) if conf[1] is socket_type],
            connect
        )
        return socket_configs
    else:
        raise ValueError("The given scheme {scheme!r} is unknown. URL: {url!r}".format(scheme=parts.scheme, url=url))
    # end if
# end def


def create_socket(url):
    socket_params = create_socket_params(url)
    s = socket.socket(socket_params.params[0])
    s.connect(socket_params.address)
    return socket_params.parts,
# end if