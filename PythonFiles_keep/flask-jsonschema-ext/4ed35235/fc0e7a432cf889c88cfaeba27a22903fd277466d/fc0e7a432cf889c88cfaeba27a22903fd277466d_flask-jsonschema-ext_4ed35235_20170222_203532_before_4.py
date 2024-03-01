from sqlalchemy import Column, Boolean, String, Integer, DateTime, BigInteger, Date
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
    def convert_entity_tree(self, entity: DeclarativeMeta, tree=None, parse_tree=None):
        if tree is None:
            tree = []

        schema = self.convert_entity(entity)
        inspection = inspect(entity)
        self._history.append(inspection.mapper)
        for relationship in inspection.relationships:
            if hasattr(inspection.class_, '__jsonschema_include__') and relationship.key not in inspection.class_.__jsonschema_include__ \
                    or parse_tree is not None and hasattr(parse_tree, '__jsonschema_include__') and relationship.key not in parse_tree.__jsonschema_include__:
                continue
            elif hasattr(inspection.class_, '__jsonschema_exclude__') and relationship.key in inspection.class_.__jsonschema_exclude__ \
                    or parse_tree is not None and hasattr(parse_tree, '__jsonschema_exclude__') and relationship.key not in parse_tree.__jsonschema_exclude__:
                continue
            elif relationship.mapper in self._history:
                # Don't go over any entities twice
                continue

            # recurse down the parse tree as we go down the entity tree
            inner_parse_tree = parse_tree[relationship.key] if parse_tree and relationship.key in parse_tree else None

            if relationship.direction == symbol('MANYTOONE'):
                schema['properties'][relationship.key] = self.convert_entity_tree(relationship.mapper, parse_tree=inner_parse_tree)
            else:
                schema['properties'][relationship.key] = {'type': 'array',
                                                          'items': self.convert_entity_tree(relationship.mapper, tree=tree + [], parse_tree=inner_parse_tree)}

        return schema

    def convert_entity(self, entity: DeclarativeMeta, parse_tree=None):
        schema = {'type': 'object', 'properties': {}, 'additionalProperties': False}
        inspection = inspect(entity)
        for field in inspection.columns:
            if hasattr(inspection.class_, '__jsonschema_include__') and field.name not in inspection.class_.__jsonschema_include__ \
                    or parse_tree is not None and hasattr(parse_tree, '__jsonschema_include__') and field.name not in parse_tree.__jsonschema_include__:
                continue
            if hasattr(inspection.class_, '__jsonschema_exclude__') and field.name in inspection.class_.__jsonschema_exclude__ \
                    or parse_tree is not None and hasattr(parse_tree, '__jsonschema_exclude__') and field.name not in parse_tree.__jsonschema_exclude__:
                continue
            schema['properties'][field.name] = self.convert_field(field)
        return schema

    def convert_field(self, field: Column):
        return field_types[type(field.type)]
