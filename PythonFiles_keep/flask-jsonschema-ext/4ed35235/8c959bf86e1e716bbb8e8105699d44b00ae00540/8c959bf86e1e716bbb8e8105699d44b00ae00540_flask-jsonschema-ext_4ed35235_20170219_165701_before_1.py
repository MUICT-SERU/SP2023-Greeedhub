from sqlalchemy import Column, Boolean, String, Integer, DateTime, BigInteger
from sqlalchemy import Date
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect
from sqlalchemy.util import symbol

from .base_driver import BaseDriver

field_types = {
    Integer: {'type': 'number'},
    BigInteger: {'type': 'number'},
    String: {'type': 'string'},
    Boolean: {'type': 'boolean'},
    Date: {'type': 'string', "format": "date"},
    DateTime: {'type': 'string', "format": "date-time"},
}


class SqlAlchemyDriver(BaseDriver):
    def convert_entity_tree(self, entity: DeclarativeMeta, tree=None):
        if tree is None:
            tree = []

        schema = self.convert_entity(entity)
        inspection = inspect(entity)
        self._history.append(inspection.mapper)
        for relationship in inspection.relationships:
            if hasattr(inspection.class_, '__jsonschema_include__') and not relationship.key in inspection.class_.__jsonschema_include__:
                continue
            if hasattr(inspection.class_, '__jsonschema_exclude__') and relationship.key in inspection.class_.__jsonschema_exclude__:
                continue
            if relationship.mapper in self._history:
                # Don't go over any entities twice
                continue
            if relationship.direction == symbol('MANYTOONE'):
                schema['properties'][relationship.key] = self.convert_entity_tree(relationship.mapper)
            else:
                schema['properties'][relationship.key] = {'type': 'array', 'items': self.convert_entity_tree(relationship.mapper, tree + [])}

        return schema

    def convert_entity(self, entity: DeclarativeMeta):
        schema = {'type': 'object', 'properties': {}, 'additionalProperties': False}
        inspection = inspect(entity)
        for field in inspection.columns:
            if hasattr(inspection.class_, '__jsonschema_include__') and not field.name in inspection.class_.__jsonschema_include__:
                continue
            if hasattr(inspection.class_, '__jsonschema_exclude__') and field.name in inspection.class_.__jsonschema_exclude__:
                continue
            schema['properties'][field.name] = self.convert_field(field)
        return schema

    def convert_field(self, field: Column):
        return field_types[type(field.type)]
