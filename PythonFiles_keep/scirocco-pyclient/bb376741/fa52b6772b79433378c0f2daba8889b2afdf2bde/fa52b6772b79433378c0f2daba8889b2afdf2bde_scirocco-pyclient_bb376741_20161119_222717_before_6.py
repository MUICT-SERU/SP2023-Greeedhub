from sciroccoclient.clientfactory import ClientFactory
from sciroccoclient.exceptions import SciroccoInitParamsError


class HTTPClient:
    def __new__(cls, *args, **kwargs):
        try:
            return ClientFactory().get_http_client(args[0], args[1], args[2])

        except IndexError:

            raise SciroccoInitParamsError
