
from sanic import Sanic
from sanic.response import json
from sanic_access_logs import AccessLogPlugin

from settings import HOST, PORT


app = Sanic(__name__)

AccessLogPlugin(app)


@app.route('/', methods=['GET'])
async def hello():
    return json({'hello': 'world'})


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, access_log=False)
