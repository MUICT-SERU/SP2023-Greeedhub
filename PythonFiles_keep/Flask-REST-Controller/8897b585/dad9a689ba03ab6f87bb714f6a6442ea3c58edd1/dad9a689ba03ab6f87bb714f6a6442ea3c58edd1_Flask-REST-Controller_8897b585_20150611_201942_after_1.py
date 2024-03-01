# coding: utf-8

try:
    import simplejson as json
except:
    import json


import urllib
import jsonschema

from flask import redirect, url_for, render_template, session, request, abort, current_app
from flask.views import MethodView


__all__ = ['BaseRender', 'JsonRender', 'TemplateRender', 'BaseHandler', 'Controller']


class BaseRender(object):
    mimetype = None

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype.lower()


class JsonRender(BaseRender):
    """
    for rendering a json response
    """
    def render_json(self, data):
        self.set_mimetype("application/json")
        if not self.is_json_response(data):
            data = [data]
        return json.dumps(data)

    def is_json_response(self, response):
        return isinstance(response, dict) or isinstance(response, list)


class TemplateRender(BaseRender):
    """
    for rendering a html template
    """
    def render_template(self, template_path, values={}):
        self.mimetype("text/html; charset=utf-8")
        return render_template(template_path, **values)


class BaseHandler(MethodView):
    """
    handling a dispatch for request
    """
    def dispatch_request(self, *args, **kwargs):
        if not self.authenticate():
            return self.authenticate_error()
        if not self.prepare():
            return self.prepare_error()

        response = super(BaseHandler, self).dispatch_request(*args, **kwargs)
        if self.should_schema_check:
            self.valid_schema(response)
        return self.after_response(response)


class Controller(TemplateRender, JsonRender, BaseHandler):
    """
    base Class based Controller implemented,
    If you want to use this class, please use to perform extends

    When there was a request to the methods, the appropriate method is run method

    example:
        HTTP GET Request -> get
        HTTP POST Request -> post
    """
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    storage = dict()
    headers = dict()
    schema = None

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.storage = dict()
        self.headers = dict()

    def add_header(self, key, value):
        self.headers[key] = value

    def get_headers(self):
        return self.headers

    @property
    def should_schema_check(self):
        """
        can verify using json schema of json response,
        """
        return True

    def valid_schema(self, response):
        if not isinstance(self.schema, list) or \
                not self.is_json_response(response):
            return response
        return jsonschema.validate(response, self.schema)

    def authenticate(self):
        """
        run validat about your authentication
        """
        return True

    def authenticate_error(self):
        """
        run for authenticate error
        """
        return self.render_error()

    def prepare(self):
        """
        prepare your validation and Update logic
        """
        return True

    def prepare_error(self):
        """
        run fot prepare error
        """
        return self.render_error()

    def get(self, *args, **kwargs):
        raise NotImplementedError()

    def post(self, *args, **kwargs):
        return self.get()

    def put(self, *args, **kwargs):
        return self.post()

    def delete(self, *args, **kwargs):
        return self.post()

    def after_response(self, response):
        return current_app.response_class(response, headers=self.get_headers(), mimetype=self.mimetype.lower())

    def render_error(self):
        return self.error_404()

    def error_404(self):
        return abort(404)

    @property
    def request(self):
        return request

    @property
    def session(self):
        return session

    @property
    def into(self):
        return self.request.method.lower()

    def redirect(self, uri, params={}):
        try:
            return redirect(url_for(uri))
        except RuntimeError:
            pass

        query = [(k, v) for k, v in sorted(params.items())]
        params = urllib.urlencode(query)
        return redirect("{0}?{1}".format(uri, params))
