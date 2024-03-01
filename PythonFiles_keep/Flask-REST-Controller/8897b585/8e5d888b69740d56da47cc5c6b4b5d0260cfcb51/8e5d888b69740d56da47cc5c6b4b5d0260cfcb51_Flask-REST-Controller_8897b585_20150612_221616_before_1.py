import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from flask_rest_controller import Controller


class HogeController(Controller):
    schema = {
        'type': 'object',
        'properties': {
            'id': {
                'type': 'string',
            },
        },
    }

    def get(self, id):
        return self.render_json({"id": id})
