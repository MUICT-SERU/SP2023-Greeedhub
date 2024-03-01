import unittest
import jinja2
from flask import Flask
from flask_rest_controller import Controller, set_routing

import json
import jsonschema

from tests.route import TEST_ROUTING_DATA

app = Flask(__name__)
app.secret_key = '\xcd\x8f\x10\x8a|\x10\t\xe8g<\xce|\xc7\xe6\xe3h\x8e\xd6\xfa\xc8i|\xee\xb0'
app.jinja_loader = jinja2.FileSystemLoader("tests/template")


class TemplateController(Controller):
    def get(self):
        return self.render_template("test.html")


class JsonController(Controller):
    schema = {
        'type': 'object',
        'properties': {
            'id': {
                'type': 'integer'
            },
            'value': {
                'type': 'string'
            },
            'request': {
                'type': 'integer'
            }
        }
    }

    def prepare(self, id):
        id = int(id)
        self.storage['request_id'] = id
        return True

    def get(self, id):
        id = self.storage['request_id']
        value = int(self.request.values.get('request'))
        return self.render_json({'id': id, 'value': "hoge", 'request': value})

    def after(self):
        self.add_header('X-REQUEST-ID', self.storage['request_id'])


class JsonArrayController(Controller):
    schema = {
        'type': 'array',
        'items': {
            'type': 'string'
        }
    }

    def get(self):
        return self.render_json(['hoge'])


class JsonSchemaInvalidController(Controller):
    schema = {
        'type': 'object',
        'properties': {
            'value': {
                'type': 'string'
            }
        }
    }

    def get(self):
        return self.render_json([1])


set_routing(app, TEST_ROUTING_DATA)


class TestController(unittest.TestCase):
    def get_response(self):
        rv = app.preprocess_request()
        if not rv:
            rv = app.dispatch_request()
            response = app.make_response(rv)
            response = app.process_response(response)
        else:
            response = app.make_response(rv)
        return response

    def test_template_controller(self):
        with app.test_request_context("/test_template_controller"):
            response = self.get_response()

            self.assertEqual(TemplateController.html_mime_type, response.mimetype)

            html = bytes("\n".join(open("tests/template/test.html").read().splitlines()), 'utf-8')
            self.assertEqual(response.data, html)

    def test_json_controller(self):
        with app.test_request_context("/test_json_controller/1?request=1000"):
            response = self.get_response()

            json_value = {'id': 1, 'value': 'hoge', 'request': 1000}
            render_json = json.dumps(json_value)

            self.assertEqual(JsonController.json_mime_type, response.mimetype)
            self.assertEqual(int(response.headers['X-REQUEST-ID']), 1)
            self.assertEqual(render_json, response.data.decode('utf-8'))

            try:
                jsonschema.validate(json_value, JsonController.schema)
            except:
                self.fail("schema is invalid")

    def test_json_array_controller(self):
        with app.test_request_context("/test_json_array_controller"):
            response = self.get_response()

            json_value = ['hoge']
            render_json = json.dumps(json_value)
            self.assertEqual(render_json, response.data.decode('utf-8'))

            try:
                jsonschema.validate(json_value, JsonArrayController.schema)
            except:
                self.fail("schema is invalid")

    def test_json_schema_invalid_controller(self):
        with app.test_request_context("/test_json_schema_invalid_controller"):
            try:
                self.get_response()
                self.fail("json schema is success")
            except jsonschema.exceptions.ValidationError:
                self.assertTrue(True)
