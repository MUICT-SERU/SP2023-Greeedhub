from flask import current_app, _app_ctx_stack
from werkzeug.contrib.profiler import ProfilerMiddleware

try:
    from flask_sqlalchemy import get_debug_queries
    flask_sqlalchemy_available = True
except ImportError:
    flask_sqlalchemy_available = False


class Profiler(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("PROFILER_ENABLED", False)
        app.config.setdefault("PROFILER_RESTRICTIONS", [])
        app.config.setdefault("PROFILER_SQLALCHEMY_ENABLED", False)
        app.config.setdefault("PROFILER_SQLALCHEMY_THRESHOLD", 0)
        app.config.setdefault("PROFILER_SQLALCHEMY_FORMAT", "statement: {query}\nparameters: {parameters}\nduration: {duration}s\ncontext: {context}\n")

        if app.config["PROFILER_ENABLED"]:
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=app.config["PROFILER_RESTRICTIONS"])

        if app.config["PROFILER_SQLALCHEMY_ENABLED"]:
            if flask_sqlalchemy_available is False:
                raise ImportError("Failed to import flask_sqlalchemy, please make sure it's installed before using the query profiler.")

            if app.config["SQLALCHEMY_RECORD_QUERIES"] is False:
                raise ValueError("SQLALCHEMY_RECORD_QUERIES is not set.")

            with app.app_context():
                app.after_request(self.__class__.log_queries)

    @staticmethod
    def log_queries(response):
        for query in get_debug_queries():
            if query.duration >= current_app.config["PROFILER_SQLALCHEMY_THRESHOLD"]:
                current_app.logger.debug(current_app.config["PROFILER_SQLALCHEMY_FORMAT"].format(dict(statement=query.statement, parameters=query.parameters, duration=query.duration, context=query.context)))

        return response