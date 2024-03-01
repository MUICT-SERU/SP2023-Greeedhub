def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

urls = ('/(.*)', hello)

import cup # importing here, just to emphasize simplicity
app = cup.application(urls)
app.run()
