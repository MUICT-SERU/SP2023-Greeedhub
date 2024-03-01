# -*- coding: utf-8 -*-
from inspire_services.orcid.conf import settings


class OrcidClient(object):
    def get_key_secret_sandbox(self):
        return settings.CONSUMER_KEY, settings.CONSUMER_SECRET, settings.DO_USE_SANDBOX
