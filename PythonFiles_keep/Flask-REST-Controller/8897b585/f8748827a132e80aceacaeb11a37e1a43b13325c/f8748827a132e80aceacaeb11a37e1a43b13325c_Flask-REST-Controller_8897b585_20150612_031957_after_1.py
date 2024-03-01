import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from flask import Flask
from flask_rest_controller import Controller, set_routing
from routes import ROUTING_VIEWS

app = Flask(__name__)
app.secret_key = '\x96hy\x96\xd6\x86\xb8#\xf0\x17\x81\n\xd8\x8a\xd3kp\x9c\xfd\xf6\x97\xf0\x89\xc8'


class IndexController(Controller):
    schema = {
        'type': 'array',
        'items': {
            'type': 'string',
        }
    }

    def get(self):
        return self.render_json(["hoge"])


set_routing(app, ROUTING_VIEWS)

if __name__ == "__main__":
    app.run(debug=True)
