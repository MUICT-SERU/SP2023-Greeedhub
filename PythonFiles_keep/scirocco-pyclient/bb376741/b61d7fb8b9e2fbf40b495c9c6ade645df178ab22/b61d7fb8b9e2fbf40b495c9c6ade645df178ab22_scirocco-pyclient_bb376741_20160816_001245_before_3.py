from pyddsclient.clientfactory import ClientFactory


class HTTPClient(object):
    def __new__(cls, *args, **kwargs):
        factory = ClientFactory()
        return factory.get_http_client(args[0], args[1])
