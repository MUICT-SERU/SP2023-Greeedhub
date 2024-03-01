# -*- coding: utf-8 -*-
import pytest

import inspire_services.orcid.conf

IS_VCR_ENABLED = True
IS_VCR_EPISODE_OR_ERROR = True  # False to record new cassettes.


def pytest_configure():
    d = dict(
        # DO_USE_SANDBOX=False,
        CONSUMER_KEY='0000-0001-8607-8906',  # Inspire official ORCID account.
        # Note: use the PROD/QA one when recording new episodes
        # You can add it to settings_local.py
        CONSUMER_SECRET='mysecret',
    )
    inspire_services.orcid.conf.settings.configure(**d)

    # Use local settings, if present.
    try:
        from .settings_local import settings_local
        inspire_services.orcid.conf.settings.configure(**settings_local)
    except ImportError:
        pass


@pytest.fixture
def vcr_config():
    if IS_VCR_EPISODE_OR_ERROR:
        record_mode = 'none'
    else:
        record_mode = 'new_episodes'

    if not IS_VCR_ENABLED:
        # Trick to disable VCR.
        return {'before_record': lambda *args, **kwargs: None}

    return {
        'decode_compressed_response': True,
        'filter_headers': ('Authorization', 'User-Agent'),
        'record_mode': record_mode,

    }


@pytest.fixture(autouse=True, scope='function')
def assert_all_played(request, vcr_cassette):
    """
    Ensure that all all episodes have been played in the current test.
    Only if the current test is marked with: @pytest.mark.vcr()
    """
    yield
    if IS_VCR_ENABLED and IS_VCR_EPISODE_OR_ERROR and request.node.get_marker('vcr'):
        assert vcr_cassette.all_played
