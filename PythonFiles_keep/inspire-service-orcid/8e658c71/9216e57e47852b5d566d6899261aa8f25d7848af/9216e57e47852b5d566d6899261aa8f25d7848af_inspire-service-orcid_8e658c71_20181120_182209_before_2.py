# -*- coding: utf-8 -*-
import time_execution
from pkgsettings import Settings as PkgSettings
from time_execution.backends.elasticsearch import ElasticsearchBackend

from inspire_service_orcid.exceptions import BaseOrcidClientJsonException

defaults = dict(
    DO_USE_SANDBOX=False,
    CONSUMER_KEY='myorcidappkey',
    CONSUMER_SECRET='myorcidappsecret',
    REQUEST_TIMEOUT=30,
    DO_ENABLE_METRICS=False,
    METRICS_BACKENDS=None,
    METRICS_ORIGIN='inspire_next',
)


def configure_time_execution(**kwargs):
    if not kwargs['DO_ENABLE_METRICS']:
        return
    backends = kwargs['METRICS_BACKENDS']
    if not backends:
        # Note: always use the sync backend when debugging, as the the async
        # thread would die too early (before actually sending the metrics).
        backends = [ElasticsearchBackend(hosts=['localhost'], index='metrics')]
    time_execution.settings.configure(
        backends=backends,
        hooks=(
            status_code_hook,
            orcid_error_code_hook,
            orcid_service_exception_hook,
        ),
        origin=kwargs['METRICS_ORIGIN'],
    )


class Settings(PkgSettings):
    def __init__(self):
        super(Settings, self).__init__()
        super(Settings, self).configure(**defaults)
        configure_time_execution(**defaults)

    def configure(self, **kwargs):
        super(Settings, self).configure(**kwargs)
        configure_time_execution(**dict(self.as_dict()))


settings = Settings()


def status_code_hook(response, exception, metric, func_args, func_kwargs):
    status_code = getattr(response, 'status_code', None)
    if status_code:
        return {'http_status_code': status_code}


def orcid_error_code_hook(response, exception, metric, func_args, func_kwargs):
    if not response or not hasattr(response, 'get'):
        return None
    data = {}
    error_code = response.get('error-code')
    if error_code:
        data['orcid_error_code'] = error_code
    developer_message = response.get('developer-message')
    if developer_message:
        data['orcid_developer_message'] = developer_message
    user_message = response.get('user-message')
    if not developer_message and user_message:
        data['orcid_user_message'] = user_message
    return data


def orcid_service_exception_hook(response, exception, metric, func_args, func_kwargs):
    if not response or not hasattr(response, 'raise_for_result'):
        return None

    try:
        response.raise_for_result()
    except BaseOrcidClientJsonException as exc:
        return {'orcid_service_exc': exc.__class__.__name__}
