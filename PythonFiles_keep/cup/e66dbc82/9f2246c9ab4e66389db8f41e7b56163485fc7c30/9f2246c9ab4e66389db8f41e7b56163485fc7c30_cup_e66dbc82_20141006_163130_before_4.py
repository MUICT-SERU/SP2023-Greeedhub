import cup
route = cup.Route()


@route('/(.*)')
class Hello:

  def GET(self, name):
    if not name:
      name = 'World'
    return 'Hello, ' + name + '!'


app = cup.application(route.urls, locals())
app.run()
