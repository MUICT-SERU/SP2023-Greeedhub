#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .blueprint_factory import bigtempo_blueprint


class BigTempoAPI(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.register_blueprint(bigtempo_blueprint())


'''
from flask import current_app

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class _Sketch(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('DATABASE', ':memory:')

        # Register teardown context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'bigtempo_instance'):
            # ctx.bigtempo_instance.close()
            pass

    def _create_instance(self):
        current_app.config['DATABASE']
        return None

    @property
    def instance(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'bigtempo_instance'):
                ctx.bigtempo_instance = None
            return ctx.bigtempo_instance
'''
