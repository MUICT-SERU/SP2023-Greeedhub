def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

urls = ('GET', '/(.*)', hello)

import cup # importing here, just to emphasize simplicity
app = cup.application(urls, locals())
app.run()
