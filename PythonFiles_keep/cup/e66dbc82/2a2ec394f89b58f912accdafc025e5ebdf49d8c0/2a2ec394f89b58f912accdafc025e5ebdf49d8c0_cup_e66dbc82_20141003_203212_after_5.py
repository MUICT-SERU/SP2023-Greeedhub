def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

urls = ('GET', '/(.*)', hello)

import dispel
app = dispel.application(urls, locals())
app.run()
