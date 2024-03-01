# -*- coding: utf-8 -*-
import pytest

import inspire_services.orcid.conf
from inspire_services.orcid import exceptions
from inspire_services.orcid.client import OrcidClient


class BaseTestOrcidClient(object):
    def setup(self):
        self.orcid = '0000-0002-0942-3697'  # Valid ORCID test account.
        try:
            # Pick the token from settings_local.py first.
            self.oauth_token = inspire_services.orcid.conf.settings.OAUTH_TOKEN
        except AttributeError:
            self.oauth_token = 'mytoken'
        self.client = OrcidClient(self.oauth_token, self.orcid)
        self.putcodes = ['46674246', '46694033']


class TestGetAllWorksSummary(BaseTestOrcidClient):
    def test_happy_flow(self):
        response = self.client.get_all_works_summary()
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['group'][0]['work-summary'][0]['put-code'] == 46674246

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.get_all_works_summary()
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.get_all_works_summary()
        with pytest.raises(exceptions.OrcidNotFoundException):
            response.raise_for_result()
        assert not response.ok


class TestGetWorksDetails(BaseTestOrcidClient):
    def test_single_putcode(self):
        response = self.client.get_works_details([self.putcodes[0]])
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['bulk'][0]['work']['put-code'] == int(self.putcodes[0])

    def test_multiple_putcodes(self):
        response = self.client.get_works_details(self.putcodes)
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['bulk'][0]['work']['put-code'] == int(self.putcodes[0])
        assert response['bulk'][1]['work']['put-code'] == int(self.putcodes[1])

    def test_too_many_putcodes(self):
        response = self.client.get_works_details([str(x) for x in range(100)])
        with pytest.raises(exceptions.ExceedMaxNumberOfPutCodesException):
            response.raise_for_result()

    def test_putcode_not_found(self):
        response = self.client.get_works_details(['xxx', self.putcodes[0]])
        with pytest.raises(exceptions.PutcodeNotFoundException):
            response.raise_for_result()

    def test_missing_putcode(self):
        with pytest.raises(ValueError):
            self.client.get_works_details([])

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.get_works_details(self.putcodes)
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.get_works_details(['12345'])
        with pytest.raises(exceptions.OrcidInvalidException):
            response.raise_for_result()
        assert not response.ok
