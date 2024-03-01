from functools import wraps, partial
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

def chunk_urls(urls, chunk_length=2):
  return map(None, *[iter(urls)]*3)

dispel_chunk_urls = partial(chunk_urls, chunk_length=3)
context_responder_urls = chunk_urls



def application(urls, env):

  def dispel_to_webpy(urls):

    def webpy_handler_class(method, pattern, handler):
      ''' dispel handler to webpy'''

      class WebPy:
        pass

      def wrap(_handler):
        def wrapped(self, *args, **kwargs):
          self.__dict__ = dict(self.__dict__.items() + web.ctx.__dict__.items())
          self.__dict__['ctx'] = web.ctx
          return _handler(self, *args, **kwargs)
        return wrapped

      handler, handler_name = isinstance(handler, str) and env[handler], handler or handler, handler.__name__
      WebPy.__dict__[method] = wrap(handler)
      env[handler_name] = WebPy
      return pattern, handler_name

    return [component
            for method, pattern, handler in dispel_chunk_urls(urls)
            for component in webpy_handler_class(method, pattern, handler) ]

  def context_responder_to_webpy(urls):

    def webpy_handler_class(pattern, Handler):
      ''' dispel Handler to webpy '''
      Handler, handler_name = isinstance(Handler, str) and env[Handler], Handler or Handler, Handler.__name__

      class WebPy(Handler):
        pass

      def wrap(_method):
        def wrapped(self, *a, **k): # will have to merge self and ctx soon
          self.__dict__ = dict(self.__dict__.items() + web.ctx.__dict__.items())
          self.__dict__['ctx'] = web.ctx
          return _method(self, *a, **k))
        return wrapped

      if hasattr(WebPy.__dict__.get('GET'), '__call__'):
        WebPy.GET = wrap(WebPy.GET)
      if hasattr(WebPy.__dict__.get('POST'), '__call__'):
        WebPy.POST = wrap(WebPy.POST)
      env[handler_name]=WebPy
      return pattern, handler_name


    return [component
            for method, pattern, handler in dispel_chunk_urls(urls)
            for component in webpy_handler_class(method, pattern, handler) ]

  def compile_to_webpy(urls):
    ''' convert to webpy format '''
    return urls[0] in ('POST', 'GET') and dispel_to_webpy(urls) or context_responder_urls(urls)

  webapp = web.application(compile_to_webpy(urls), env)
  webapp.add_processor(web.loadhook(hook_less(webapp)))
  return webapp


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
