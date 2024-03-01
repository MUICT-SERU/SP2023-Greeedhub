import dispel
route = dispel.Route()

@route('/(.*)')
class Hello:

  def GET(self, name):
    if not name:
      name = 'World'
    return 'Hello, ' + name + '!'

app = dispel.application(route.urls, locals())
app.run()
