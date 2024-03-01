# -*- coding: utf-8 -*-
import pytest

import inspire_services.orcid.conf
from inspire_services.orcid import exceptions
from inspire_services.orcid.client import OrcidClient


class TestGetAllWorksSummary(object):
    def setup(self):
        self.orcid = '0000-0002-0942-3697'  # Valid ORCID test account.
        try:
            # Pick the token from settings_local.py first.
            self.oauth_token = inspire_services.orcid.conf.settings.OAUTH_TOKEN
        except AttributeError:
            self.oauth_token = 'mytoken'
        self.client = OrcidClient(self.oauth_token, self.orcid)

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
