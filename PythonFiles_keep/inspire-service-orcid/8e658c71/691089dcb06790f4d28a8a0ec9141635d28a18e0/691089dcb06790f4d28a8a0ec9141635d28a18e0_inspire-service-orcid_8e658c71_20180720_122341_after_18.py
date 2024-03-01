import inspire_services.orcid.conf


def pytest_configure():
    d = dict(
        # DO_USE_SANDBOX=False,
        CONSUMER_KEY='key',
        CONSUMER_SECRET='secret',
    )
    inspire_services.orcid.conf.settings.configure(**d)
