import dispel


class Hello:

  def GET(self, name):
    if not name:
      name = 'World'
    return 'Hello, ' + name + '!'


urls = ('/(.*)', Hello)
app = dispel.application(urls, locals())
app.run()

