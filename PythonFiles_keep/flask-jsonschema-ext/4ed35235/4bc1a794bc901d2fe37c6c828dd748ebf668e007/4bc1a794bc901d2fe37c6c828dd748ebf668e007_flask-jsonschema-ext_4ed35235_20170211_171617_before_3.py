from functools import wraps

from .drivers.sqlalchemy import convert_entity


def schema_json(database_entity):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            convert_entity(database_entity)
            return func(*args, **kwargs)
        return wrapper
    return decorator
