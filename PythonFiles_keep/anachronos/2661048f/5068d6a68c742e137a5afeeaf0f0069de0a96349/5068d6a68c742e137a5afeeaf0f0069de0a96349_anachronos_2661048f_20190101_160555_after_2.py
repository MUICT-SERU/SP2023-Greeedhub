class AnachronosException(BaseException):
    pass


class AnachronosAssertionException(AnachronosException):
    def __init__(self, message: str):
        self.message = message
