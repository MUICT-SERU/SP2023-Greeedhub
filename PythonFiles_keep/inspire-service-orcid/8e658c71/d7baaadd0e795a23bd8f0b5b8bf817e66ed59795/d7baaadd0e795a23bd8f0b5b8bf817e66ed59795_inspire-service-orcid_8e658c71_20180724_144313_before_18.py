#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inspire_services.orcid.client import OrcidClient


class TestOrcidClient(object):
    def test_get_key_secret_sandbox(self):
        client = OrcidClient()
        key, secret, sandbox = client.get_key_secret_sandbox()
        assert key == 'key'
        assert secret == 'secret'
        assert not sandbox
