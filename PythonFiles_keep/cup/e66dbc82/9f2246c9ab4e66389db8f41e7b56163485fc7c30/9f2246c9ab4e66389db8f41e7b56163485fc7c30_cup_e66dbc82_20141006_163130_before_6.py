import cup


class Hello:

  def GET(self, name):
    if not name:
      name = 'World'
    return 'Hello, ' + name + '!'


urls = ('/(.*)', Hello)
app = cup.application(urls, locals())
app.run()

