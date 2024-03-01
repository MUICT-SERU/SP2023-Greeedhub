def hello(ctx, name):
  if not name:
    name = 'World'
  return 'Hello, ' + name + '!'

def only_hello(ctx):
  return 'Hello!'

def save_message(ctx, name):
  message = hello(ctx, name)
  # save name in database
  return message

urls = (
  '/(.*)', hello,
  'POST', '/(.*)', save_message,
  'GET', 'only_hello', only_hello
)

import cup # importing here, just to emphasize simplicity
app = cup.application(urls)
app.run()
