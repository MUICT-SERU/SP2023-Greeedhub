from client.clientfactory import ClientFactory


class HTTPClient(object):

    def __init__(self, node_id, auth_token):

        self.node_id = node_id
        self.auth_token = auth_token

    def __new__(cls, *args, **kwargs):

        factory = ClientFactory()
        return factory.get_http_client(cls.node_id, cls.auth_token)
