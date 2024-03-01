class Hello:

  def GET(self, name):
    if not name:
      name = 'World'
    return 'Hello, ' + name + '!'

urls = ('/(.*)', Hello)

import cup
app = cup.application(urls)
app.run()

