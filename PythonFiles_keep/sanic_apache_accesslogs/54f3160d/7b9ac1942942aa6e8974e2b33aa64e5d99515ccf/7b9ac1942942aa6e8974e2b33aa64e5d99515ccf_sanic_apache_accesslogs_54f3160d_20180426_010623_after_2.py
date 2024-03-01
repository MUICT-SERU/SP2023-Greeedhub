from .plugin import accesslog_plugin

from sanic.response import HTTPResponse


@accesslog_plugin.middleware(attach_to='response',
                             relative='post',
                             with_context=True)
def print_access_log(request, response, context):
    """Log the entry."""
    logger = context['logger']
    if request is None:  # no request, do nothing
        return response

    extra = {
        'h': '-',
        'l': '-',
        'q': '',
        's': getattr(response, 'status', 0),
        'u': '-',
        'H': '-',
        'Referer': '-',
        'User-Agent': '-'
    }

    if isinstance(response, HTTPResponse):
        extra['b'] = len(response.body)
    else:
        extra['b'] = -1

    if request.ip:
        extra['h'] = request.ip

    if 'user' in request:
        extra['u'] = request.user

    if request.remote_addr:
        extra['h'] = request.remote_addr

    extra['m'] = request.method
    extra['U'] = request.path
    if request.query_string:
        extra['q'] = '?{}'.format(request.query_string)
    extra['H'] = 'HTTP/{}'.format(request.version)

    if 'User-Agent' in request.headers:
        extra['User-Agent'] = request.headers['User-Agent']
    if 'Referer' in request.headers:
        extra['Referer'] = request.headers['Referer']
    # log the access
    logger.info('', extra=extra)
    return response
