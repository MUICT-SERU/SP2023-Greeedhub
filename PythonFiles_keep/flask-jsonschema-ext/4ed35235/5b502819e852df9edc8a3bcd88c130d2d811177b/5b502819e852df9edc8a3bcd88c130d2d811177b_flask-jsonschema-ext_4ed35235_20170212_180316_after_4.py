from sqlalchemy import Column, Boolean, String, Integer
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect
from sqlalchemy.util import symbol

from .base_driver import BaseDriver

field_types = {
    Integer: 'number',
    String: 'string',
    Boolean: 'boolean',
}


class SqlAlchemyDriver(BaseDriver):
    def convert_entity_tree(self, entity: DeclarativeMeta, tree=None):
        if tree is None:
            tree = []

        schema = self.convert_entity(entity)
        inspection = inspect(entity)
        self._history.append(inspection.mapper)
        for relationship in inspection.relationships:
            if relationship.mapper in self._history:
                # Don't go over any entities twice
                continue
            if relationship.direction == symbol('MANTTOONE'):
                schema[relationship.back_populates] = {'type': 'array', 'items': self.convert_entity_tree(relationship.mapper, tree + [])}
            else:
                schema[relationship.key] = {'type': 'object', 'items': self.convert_entity_tree(relationship.mapper)}

        return schema

    def convert_entity(self, entity: DeclarativeMeta):
        schema = {'type': 'object', 'properties': {}}
        inspection = inspect(entity)
        for field in inspection.columns:
            schema['properties'][field.name] = self.convert_field(field)
        return schema

    def convert_field(self, field: Column):
        return {'type': field_types[type(field.type)]}
