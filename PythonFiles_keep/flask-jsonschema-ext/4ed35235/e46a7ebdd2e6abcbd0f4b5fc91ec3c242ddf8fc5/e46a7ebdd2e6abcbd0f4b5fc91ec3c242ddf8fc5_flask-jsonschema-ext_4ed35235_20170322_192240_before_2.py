from functools import partial
from functools import wraps

from flask import current_app
from jsonschema import validate
from flask import request
from werkzeug.local import LocalProxy

from .drivers.base_driver import BaseDriver

__version__ = '0.1.2'

_fja = LocalProxy(lambda: current_app.extensions['flask_jsonschema_ext'])


def schema_json(database_entity, parse_tree=None, cached=True):
    def decorator(func, cache=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if cached and cache is not None:
                try:
                    schema = cache['schema']
                except KeyError:
                    schema = _fja.driver().convert_entity_tree(database_entity, parse_tree=parse_tree)
                    cache['schema'] = schema
            else:
                schema = _fja.driver().convert_entity_tree(database_entity, parse_tree=parse_tree)

            validate(request.get_json(), schema)
            return func(*args, **kwargs)

        return wrapper

    if cached is True:
        return partial(decorator, cache={})
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


class FlaskJsonSchemaExt(object):
    def __init__(self, app=None, driver=None, **kwargs):
        if app is not None:
            self._state = self.init_app(app, driver, **kwargs)

    def init_app(self, app, driver, **kwargs):
        state = _get_state(app, driver, **kwargs)
        app.extensions['flask_jsonschema_ext'] = state
        return state
