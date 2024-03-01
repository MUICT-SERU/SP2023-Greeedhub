import dispel

route = dispel.Route()

@route.GET('/(.*)')
def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

app = dispel.application(route.urls, locals())
app.run()

