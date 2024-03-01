__all__ = ['config', 'db', 'template', 'form', 'application', 'Route',
           'debugerror','http', 'httpserver', 'net', 'utils']

import inspect
import web

config = web.config
db = web.db
template = web.template
form = web.form
debugerror = web.debugerror
http = web.http
httpserver = web.httpserver
net = web.net
utils = web.utils

web_api = web.webapi.__dict__

def session_store_not_configured(self):
  raise Exception('Session Store not configured')

def application(urls, **k):
  ''' a web.py application generator '''
  env = {}

  def generate_webpy_from_handler(method, pattern, handler):
    class Handler:
      pass
    # raises exception to inform that session store is not configured
    Handler.session = property(session_store_not_configured)

    def wrap_request_handler(handler):
      ''' takes a cup method and returns web.py handler '''
      def wrapped_handler(instance, *a, **k):
        ''' a handler GET or POST or BOTH method'''
        instance.__dict__ = dict( web.ctx.__dict__.items() + web_api.items() + instance.__dict__.items())
        if web.config.get('session_store'): instance.session = session
        return handler(instance, *a, **k)
      return wrapped_handler
    if method is 'BOTH':
      Handler.__dict__['GET'] = Handler.__dict__['POST'] = wrap_request_handler(handler)
    else:
      Handler.__dict__[method] = wrap_request_handler(handler)
    env[handler.__name__] = Handler
    return pattern, handler.__name__

  def generate_webpy_from_handler_class(pattern, _Handler):
    ''' cup Handler to webpy handler'''

    class Handler(_Handler):
      pass
    Handler.session = property(session_store_not_configured)
    def wrap(_method):
      def wrapped(self, *a, **k): # will have to merge self and ctx soon
        self.__dict__ = dict(self.__dict__.items() + web.ctx.__dict__.items() + web_api.items())
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
  session = web.config.get('session_store') and web.session.Session(app, web.config.session_store) or {}
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
