from inspire_service_orcid.exceptions import BaseOrcidClientJsonException


def status_code_hook(response, exception, metric, func_args, func_kwargs):
    """
    @time_execution hook to collect the HTTP status code from a response.
    """
    status_code = getattr(response, 'status_code', None)
    if status_code:
        return {'http_status_code': status_code}


def orcid_error_code_hook(response, exception, metric, func_args, func_kwargs):
    """
    @time_execution hook to collect the orcid error code from an orcid's api
    response.
    """
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
    """
    @time_execution hook to collect info regarding an orcid exception.
    """
    if not response or not hasattr(response, 'raise_for_result'):
        return None

    try:
        response.raise_for_result()
    except BaseOrcidClientJsonException as exc:
        return {'orcid_service_exc': exc.__class__.__name__}
