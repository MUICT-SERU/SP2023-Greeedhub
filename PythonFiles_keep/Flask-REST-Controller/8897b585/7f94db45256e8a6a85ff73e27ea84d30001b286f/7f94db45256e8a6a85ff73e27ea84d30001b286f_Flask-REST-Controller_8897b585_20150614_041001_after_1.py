import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from flask_rest_controller import Controller


class HogeController(Controller):
    schema = {
        'get': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                },
            },
        },
        'post': {
            'type': 'object',
            'properties': {
                'result': {
                    'type': 'string',
                },
                'code': {
                    'type': 'integer',
                }
            },
        }
    }

    def prepare(self, id):
        self.storage['hoge_id'] = int(id)
        return True

    def get(self, id):
        id = self.storage['hoge_id']
        return self.render_json({"id": id})

    def post(self, id):
        return self.render_json({"result": "OK", "code": 200})

    def after(self):
        id = self.storage['hoge_id']
        self.add_header("X-HOGE-ID", id)
