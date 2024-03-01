# -*- coding: utf-8 -*-
import re


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


class TokenMismatchException(BaseOrcidClientJsonException):
    http_status_code = 401
    content = {
        'error-code': 9017
    }


class OrcidNotFoundException(BaseOrcidClientJsonException):
    http_status_code = 404
    content = {
        'error-code': 9016
    }

    @classmethod
    def match(cls, response):
        if not super(OrcidNotFoundException, cls).match(response):
            return False

        return re.search(r'ORCID iD .* not found', response['developer-message'], re.I)


class OrcidInvalidException(BaseOrcidClientJsonException):
    http_status_code = 500
    content = {
        'error-code': 9008
    }


class GenericGetWorksDetailsException(BaseOrcidClientJsonException):
    http_status_code = 200

    @classmethod
    def match(cls, response):
        result = response.status_code == cls.http_status_code
        if not result:
            return False

        for work in response.get('bulk', []):
            if 'error' in work:
                return True
        return False


class PutcodeNotFoundGetException(BaseOrcidClientJsonException):
    http_status_code = 200

    @classmethod
    def match(cls, response):
        result = response.status_code == cls.http_status_code
        if not result:
            return False

        for work in response.get('bulk', []):
            if work.get('error', {}).get('error-code', None) == 9034:
                return True
        return False


class PutcodeNotFoundPutException(BaseOrcidClientJsonException):
    http_status_code = 404
    content = {
        'error-code': 9016
    }


class ExceedMaxNumberOfPutCodesException(BaseOrcidClientJsonException):
    http_status_code = 400
    content = {
        'error-code': 9042
    }


class WorkAlreadyExistentException(BaseOrcidClientJsonException):
    http_status_code = 409
    content = {
        'error-code': 9021
    }


class InvalidDataException(BaseOrcidClientJsonException):
    http_status_code = 400
    content = {
        'error-code': 9001
    }


class TokenWithWrongPermissionException(BaseOrcidClientJsonException):
    http_status_code = 403
    content = {
        'error-code': 9038
    }
