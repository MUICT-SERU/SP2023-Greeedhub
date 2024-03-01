import inspect
import web

def hook_less(app):
  def _hook():
    if web.config.get('session_store'): web.ctx.session = web.session.Session(app, web.config.session_store)
    web.ctx.setcookie = web.setcookie
    web.ctx.cookies = web.cookies
    web.ctx.input = web.input
    web.ctx.header = web.header
    web.ctx.data = web.data
  return _hook

def application(urls, **k):
  env = {}

  def generate_webpy_from_handler(method, pattern, handler):
    class Handler:
      pass

    def wrap_request_handler(handler):
      def wrapped_handler(instance, *a, **k):
        instance.__dict__ = dict(instance.__dict__.items() + web.ctx.__dict__.items())
        return handler(instance, *a, **k)
      return wrapped_handler
    if method is 'BOTH':
      Handler.__dict__['GET'] = Handler.__dict__['POST'] = wrap_request_handler(handler)
    else:
      Handler.__dict__[method] = wrap_request_handler(handler)
    env[handler.__name__] = Handler
    return pattern, handler.__name__

  def generate_webpy_from_handler_class(pattern, _Handler):
    ''' dispel Handler to webpy '''

    class Handler(_Handler):
      pass

    def wrap(_method):
      def wrapped(self, *a, **k): # will have to merge self and ctx soon
        self.__dict__ = dict(self.__dict__.items() + web.ctx.__dict__.items())
        self.__dict__['web'] = web.ctx
        return _method(self, *a, **k)
      return wrapped

    if hasattr(_Handler.__dict__.get('GET'), '__call__'):
      Handler.GET = wrap(_Handler.GET)
    if hasattr(_Handler.__dict__.get('POST'), '__call__'):
      Handler.POST = wrap(_Handler.POST)
    env[_Handler.__name__] = Handler
    return pattern, _Handler.__name__

  def handler_for_urls(urls):
    url_handlers = []
    while urls:
      chunk = urls[:3]
      if chunk[0] not in ('GET', 'POST'):
        if inspect.isfunction(chunk[1]):
          pattern, name = generate_webpy_from_handler('BOTH', chunk[0], chunk[1])
          urls = urls[2:]
        else:
          pattern, name = generate_webpy_from_handler_class(chunk[0], chunk[1])
          urls = urls[2:]
      else:
        pattern, name = generate_webpy_from_handler(chunk[0], chunk[1], chunk[2])
        urls = urls[3:]
      url_handlers += [pattern, name]
    return url_handlers

  app = web.application(handler_for_urls(urls), env, **k)
  app.add_processor(web.loadhook(hook_less(app)))
  return app

class Route:

  def __init__(self):
    self._urls = []

  def GET(self, pattern, **k):
    def _get(f):
      self._urls += ['GET', pattern, f]
      return f
    return _get

  def POST(self, pattern, **k):
    def _post(f):
      self._urls += ['POST', pattern, f]
      return f
    return _post

  @property
  def urls(self):
    return self._urls

  def __call__(self, pattern, **k):
    def _call(c):
      self._urls += [pattern, c]
      return c
    return _call
