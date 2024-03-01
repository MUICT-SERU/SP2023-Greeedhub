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


def chunk_urls(urls):
  return map(None, *[iter(urls)]*3)

def application(urls, env):
  def webpy_handler_class(method, pattern, handler):
    ''' convert functional view to class based view consumable by default webpy application'''
    class _Handler:
      pass
    def wrap(_handler):
      def wrapped(self, *args, **kwargs):
        return _handler(web.ctx, *args, **kwargs)
      return wrapped
    _Handler.__dict__[method] = wrap(handler)
    env[handler.__name__] = _Handler
    return pattern, handler.__name__
  def compile_to_webpy(urls):
    ''' convert to webpy format '''
    return [component
            for method, pattern, handler in urls
            for component in webpy_handler_class(method, pattern, handler) ]
  webapp = web.application(compile_to_webpy(chunk_urls(urls)), env)
  webapp.add_processor(web.loadhook(hook_less(webapp)))
  return webapp
