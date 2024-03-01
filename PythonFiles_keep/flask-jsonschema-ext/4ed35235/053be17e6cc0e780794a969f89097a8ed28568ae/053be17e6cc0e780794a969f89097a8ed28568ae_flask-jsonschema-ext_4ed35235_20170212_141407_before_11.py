from sqlalchemy import Column, Boolean, String, Integer
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect

field_types = {
    Integer: 'number',
    String: 'string',
    Boolean: 'boolean',
}


def convert_entity(entity: DeclarativeMeta):
    schema = {'type': 'object', 'properties': {}}
    for field in inspect(entity).columns:
        schema['properties'][field.name] = convert_field(field)
    return schema


def convert_field(field: Column):
    return {'type': field_types[type(field.type)]}
