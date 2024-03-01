# -*- coding: utf-8 -*-
from inspire_services.orcid import exceptions

from six import MovedModule, add_move  # isort:skip
add_move(MovedModule('mock', 'mock', 'unittest.mock'))
from six.moves import mock  # noqa:E402 isort:skip


class MyExcpetion(exceptions.BaseOrcidClientJsonException):
    http_status_code = 401
    content = {
        'error': 'invalid_token'
    }


def test_match_positive():
    response = mock.MagicMock()
    response.status_code = 401
    response.get.return_value = 'invalid_token'
    assert MyExcpetion.match(response)


def test_match_negative_content():
    response = mock.MagicMock()
    response.status_code = 401
    response.get.return_value = 'xxx'
    assert not MyExcpetion.match(response)


def test_match_negative_status_code():
    response = mock.MagicMock()
    response.status_code = 400
    response.get.return_value = 'invalid_token'
    assert not MyExcpetion.match(response)
