# -*- coding: utf-8 -*-
from pkgsettings import Settings

settings = Settings()
settings.configure(
    DO_USE_SANDBOX=False,
    CONSUMER_KEY='myorcidappkey',
    CONSUMER_SECRET='myorcidappsecret',
    REQUEST_TIMEOUT=30,
)
