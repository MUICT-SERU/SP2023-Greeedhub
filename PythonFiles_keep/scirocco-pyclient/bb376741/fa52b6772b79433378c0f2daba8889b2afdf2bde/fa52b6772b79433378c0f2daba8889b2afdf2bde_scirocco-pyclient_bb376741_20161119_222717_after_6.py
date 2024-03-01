from sciroccoclient.clientfactory import ClientFactory
from sciroccoclient.exceptions import SciroccoInitParamsError


class HTTPClient:
    """
        :param api_url: string
            scirocco instance to connect to.
        :param node_id: string
            identify this instance as a node of the system.
        :param auth_token: string
            Token that authorizes this node to access the server.
        :return: Client intance.
    """

    def __new__(cls, *args, **kwargs):
        try:
            return ClientFactory().get_http_client(args[0], args[1], args[2])

        except IndexError:

            raise SciroccoInitParamsError
