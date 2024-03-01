# coding: utf-8

try:
    import simplejson as json
except:
    import json

import urllib

from flask import redirect, url_for, render_template, session, request, abort, current_app
from flask.views import MethodView


__all__ = ['BaseRender', 'JsonRender', 'TemplateRender', 'BaseHandler', 'Controller']


class BaseRender(object):
    mimetype = None


class JsonRender(BaseRender):
    def render_json(self, data):
        self.mimetype = "application/json"
        if not isinstance(data, dict) or not isinstance(data, list):
            data = [data]
        return json.dumps(data)


class TemplateRender(BaseRender):
    def render_template(self, template_path, values={}):
        self.mimetype = "text/html; charset=utf-8"
        return render_template(template_path, **values)


class BaseHandler(MethodView):
    def dispatch_request(self, *args, **kwargs):
        if not self.authenticate():
            return self.authenticate_error()
        if not self.prepare():
            return self.prepare_error()

        response = super(BaseHandler, self).dispatch_request(*args, **kwargs)
        return self.after_response(response)


class Controller(TemplateRender, JsonRender, BaseHandler):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    storage = dict()
    headers = dict()

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.storage = dict()
        self.headers = dict()

    def add_header(self, key, value):
        self.headers[key] = value

    def get_headers(self):
        return self.headers

    def authenticate(self):
        return True

    def authenticate_error(self):
        return self.render_error()

    def prepare(self):
        return True

    def prepare_error(self):
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
        url = "{0}?{1}".format(uri, params)
        return redirect(url)
