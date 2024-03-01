def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

urls = ('GET', '/(.*)', hello)

import dispel # importing here, just to emphasize simplicity
app = dispel.application(urls, locals())
app.run()
