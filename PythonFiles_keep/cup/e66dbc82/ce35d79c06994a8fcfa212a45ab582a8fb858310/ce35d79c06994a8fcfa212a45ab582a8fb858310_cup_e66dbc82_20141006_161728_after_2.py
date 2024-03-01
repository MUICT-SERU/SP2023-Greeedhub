import cup

route = cup.Route()

@route.GET('/(.*)')
def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

app = cup.application(route.urls)
app.run()

