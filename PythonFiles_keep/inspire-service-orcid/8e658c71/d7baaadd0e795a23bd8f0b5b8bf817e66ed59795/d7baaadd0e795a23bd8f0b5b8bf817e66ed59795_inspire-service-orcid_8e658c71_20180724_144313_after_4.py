# -*- coding: utf-8 -*-


class BaseOrcidClientJsonException(Exception):
    http_status_code = 500
    content = {}

    @classmethod
    def match(cls, response):
        result = response.status_code == cls.http_status_code
        for key, value in cls.content.items():
            if not result:
                return False
            result = result and (
                response.get(key, None) == value
            )
        return result


class TokenInvalidException(BaseOrcidClientJsonException):
    http_status_code = 401
    content = {
        'error': 'invalid_token'
    }


class OrcidNotFoundException(BaseOrcidClientJsonException):
    http_status_code = 404
    content = {
        'error-code': 9016
    }
