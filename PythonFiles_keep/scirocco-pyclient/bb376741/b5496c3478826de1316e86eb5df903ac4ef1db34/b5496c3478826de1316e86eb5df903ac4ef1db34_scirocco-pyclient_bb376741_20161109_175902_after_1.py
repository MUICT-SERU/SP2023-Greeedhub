class SciroccoError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class SciroccoRequestAdapterError(SciroccoError):
    """ Raised when theres some problem at request low level. Probably the request manager aka urllib3 changed its behaviour
        or something else.
    """

    def __init__(self, message):
        super(SciroccoRequestAdapterError, self).__init__(message)


class SciroccoInitParamsError(SciroccoError):
    """
        Raised when thers an unexpected result in DAO layer.
    """

    def __init__(self):
        message = "You must init your connection to scirocco server with three positional arguments, host, node_id and auth_token."
        super(SciroccoInitParamsError, self).__init__(message)

class SciroccoHTTPDAOError(SciroccoError):
    """
        Raised when thers an unexpected result in DAO layer.
    """

    def __init__(self, message):

        message = ''.join(["HTTPDAO received an unexpected status code ", str(message)])

        super(SciroccoHTTPDAOError, self).__init__(message)


