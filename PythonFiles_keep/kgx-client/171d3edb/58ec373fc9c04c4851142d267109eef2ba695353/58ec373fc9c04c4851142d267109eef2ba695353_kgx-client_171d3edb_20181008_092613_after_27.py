from enum import Enum
from http import HTTPStatus


class APIExceptionType(Enum):
    """ Returned from KGX in JSON to identify the specific problem that has occurred.
    """
    api_exception = 'APIException'
    bad_address_exception = 'BadAddressException'
    auth_exception = 'AuthException'
    estimate_expired_exception = 'EstimateExpiredException'
    fatal_exception = 'FatalException'
    not_found_exception = 'NotFoundException'
    undeliverable_exception = 'UndeliverableException'
    uri_exception = 'URIException'


class KGXExceptionBase(Exception):
    """ Base class for any errors raised by the KGX API.
    """


class APIErrorResponse(KGXExceptionBase):
    """ The API was contactable, but the request could not be processed for some reason.
    """
    __slots__ = ['message', 'kind', 'code', ]

    def __init__(self, message: str, kind: APIExceptionType, code: HTTPStatus):
        self.message = message
        self.kind = kind
        self.code = code

    @classmethod
    def from_api_json(cls, api_json: dict):
        return cls(
            message=api_json['error']['message'],
            kind=APIExceptionType(api_json['error']['kind']),
            code=api_json['error']['code']
        )

    def __str__(self):
        return f'<APIErrorResponse({self.code}, {self.kind})>'


class APINotContactable(KGXExceptionBase):
    """ Raised when the HTTP client cannot communicate with KGX.
    """
    def __init__(self, inner_exception):
        self.inner_exception = inner_exception

    def __str__(self):
        return str(self.inner_exception)


class APIResponseNotJson(KGXExceptionBase):
    """ Raised if the API response is not valid JSON.
    """
    def __init__(self, inner_exception):
        self.inner_exception = inner_exception

    def __str__(self):
        return str(self.inner_exception)
