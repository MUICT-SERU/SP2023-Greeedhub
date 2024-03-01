from sqlalchemy import Column, Boolean, String, Integer
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect

from .base_driver import BaseDriver

field_types = {
    Integer: 'number',
    String: 'string',
    Boolean: 'boolean',
}


class SqlAlchemyDriver(BaseDriver):
    @classmethod
    def convert_entity_tree(cls, entity: DeclarativeMeta):
        schema = cls.convert_entity(entity)
        inspection = inspect(entity)
        definitions = {}
        for relationship in inspection.relationships:
            pass
        return schema

    @classmethod
    def convert_entity(cls, entity: DeclarativeMeta):
        schema = {'type': 'object', 'properties': {}}
        inspection = inspect(entity)
        for field in inspection.columns:
            schema['properties'][field.name] = cls.convert_field(field)
        return schema

    @classmethod
    def convert_field(cls, field: Column):
        return {'type': field_types[type(field.type)]}
