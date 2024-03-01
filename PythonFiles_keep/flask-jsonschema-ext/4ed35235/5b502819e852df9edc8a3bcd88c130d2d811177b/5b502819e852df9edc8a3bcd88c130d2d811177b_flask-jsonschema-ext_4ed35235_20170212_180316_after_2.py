from functools import wraps

from flask import current_app
from jsonschema import validate
from flask import request
from werkzeug.local import LocalProxy

from .drivers.base_driver import BaseDriver

_fja = LocalProxy(lambda: current_app.extensions['flask_jsonschema_alt'])


def schema_json(database_entity):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validate(request.get_json(), _fja.driver().convert_entity_tree(database_entity))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_state(app, driver, **kwargs):
    kwargs.update(dict(
        app=app,
        driver=driver,
    ))

    return _State(**kwargs)


class _State(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)


class FlaskJsonSchemaAlt(object):
    def __init__(self, app=None, driver: BaseDriver = None, **kwargs):
        if app is not None:
            self._state = self.init_app(app, driver, **kwargs)

    def init_app(self, app, driver, **kwargs):
        state = _get_state(app, driver, **kwargs)
        app.extensions['flask_jsonschema_alt'] = state
        return state
