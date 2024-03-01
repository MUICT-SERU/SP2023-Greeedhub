# -*- coding: utf-8 -*-
import pytest
from requests.exceptions import HTTPError

from inspire_services.orcid import exceptions, models

from six import MovedModule, add_move  # isort:skip
add_move(MovedModule('mock', 'mock', 'unittest.mock'))
from six.moves import mock  # noqa:E402 isort:skip


class TestBaseOrcidClientResponse(object):
    def setup(self):
        self.data = {'color': 'red', 'age': 25}
        self.memberapi_mock = mock.Mock()
        self.memberapi_mock.raw_response.ok = True
        self.memberapi_mock.raw_response.status_code = 200

    def test_dict_response(self):
        response = models.BaseOrcidClientResponse(self.memberapi_mock, self.data)
        assert response['color'] == self.data['color']
        assert response['age'] == self.data['age']
        assert response.raw_response == self.memberapi_mock.raw_response
        assert response.status_code == 200
        assert response.request == self.memberapi_mock.raw_response.request
        assert response.ok

    def test_response(self):
        from requests.models import Response
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.json = lambda: self.data

        response = models.BaseOrcidClientResponse(self.memberapi_mock, mock_response)
        assert response['color'] == self.data['color']
        assert response['age'] == self.data['age']
        assert response.raw_response == mock_response
        assert response.status_code == 200
        assert response.ok

    def test_raise_valueerror(self):
        with pytest.raises(ValueError):
            models.BaseOrcidClientResponse(self.memberapi_mock, ['wrongtype'])

    def test_raise_for_result_status_code(self):
        self.memberapi_mock.raw_response.status_code = 404
        self.memberapi_mock.raw_response.raise_for_status.side_effect = HTTPError
        response = models.BaseOrcidClientResponse(self.memberapi_mock, self.data)
        with pytest.raises(HTTPError):
            response.raise_for_result()

    def test_raise_for_result_exception_matched(self):
        self.memberapi_mock.raw_response.status_code = 401
        self.data['error'] = 'invalid_token'
        response = models.BaseOrcidClientResponse(self.memberapi_mock, self.data)
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()

    def test_raise_for_result_exception_unmatched_and_200(self):
        self.memberapi_mock.raw_response.status_code = 200
        response = models.BaseOrcidClientResponse(self.memberapi_mock, self.data)
        response.raise_for_result()  # Should not raise.
        self.memberapi_mock.raw_response.raise_for_status.assert_called()
