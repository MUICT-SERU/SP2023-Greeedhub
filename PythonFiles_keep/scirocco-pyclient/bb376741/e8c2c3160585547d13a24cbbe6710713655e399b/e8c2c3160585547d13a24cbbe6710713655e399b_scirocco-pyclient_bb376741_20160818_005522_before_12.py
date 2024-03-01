from pyddsclient.clientfactory import ClientFactory


class HTTPClient:
    def __new__(cls, *args, **kwargs):
        return ClientFactory().get_http_client(args[0], args[1], args[2])
