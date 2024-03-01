from functools import partial
from functools import wraps

from flask import current_app
from jsonschema import validate
from flask import request
from werkzeug.local import LocalProxy

_fja = LocalProxy(lambda: current_app.extensions['flask_jsonschema_ext'])


def generate_jsonschema(database_entity, parse_tree=None):
    """Generate a JSONSchema from a database entity"""
    return _fja.driver().convert_entity_tree(database_entity, parse_tree=parse_tree)


def jsonschema(schema_generation_fn, cached=True):
    """Decorate a method to be protected by a jsonschema using the schema generation function specified"""

    def decorator(func, cache=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the schema from the cache or generate it
            if cached and cache is not None:
                try:
                    schema = cache['schema']
                except KeyError:
                    schema = schema_generation_fn()
                    cache['schema'] = schema
            else:
                schema = schema_generation_fn()

            # Validate the request as it comes in
            validate(request.get_json(), schema)
            return func(*args, **kwargs)

        return wrapper

    if cached is True:
        return partial(decorator, cache={})
    return decorator


def jsonschema_generate(database_entity, cached=True, parse_tree=None):
    """Shorthand for protecting a method with jsonschema and using generate_jsonschema on a database entity"""
    return jsonschema(partial(generate_jsonschema, database_entity, parse_tree=parse_tree), cached=cached)


# Deprecated, here for backwards compatibility with 0.1.2
# TODO: remove in 1.0.0
schema_json = jsonschema_generate


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
