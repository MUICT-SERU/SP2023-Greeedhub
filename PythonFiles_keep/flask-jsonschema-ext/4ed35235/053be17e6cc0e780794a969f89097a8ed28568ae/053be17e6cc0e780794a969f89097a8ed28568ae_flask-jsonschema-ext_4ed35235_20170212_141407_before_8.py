from functools import wraps

from jsonschema import validate
from flask import request

from .drivers.sqlalchemy import convert_entity


def schema_json(database_entity):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validate(request.get_json(), convert_entity(database_entity))
            return func(*args, **kwargs)

        return wrapper

    return decorator
