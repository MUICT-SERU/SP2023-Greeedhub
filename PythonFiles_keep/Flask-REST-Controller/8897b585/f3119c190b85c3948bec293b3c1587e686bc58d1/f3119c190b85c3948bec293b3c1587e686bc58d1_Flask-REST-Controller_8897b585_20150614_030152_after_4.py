import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from flask_rest_controller import Controller


class TemplateController(Controller):
    def prepare(self):
        id = self.request.values.get('id')
        if not id:
            id = 1
        self.storage['id'] = id
        return True

    def get(self):
        id = self.storage['id']
        return self.render_template("template.html", {"id": id})
