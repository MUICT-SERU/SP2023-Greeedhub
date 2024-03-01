import dispel

route = dispel.Route()

@route.GET('/(.*)')
def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

print route._urls

app = dispel.application(route.urls, locals())
app.run()

