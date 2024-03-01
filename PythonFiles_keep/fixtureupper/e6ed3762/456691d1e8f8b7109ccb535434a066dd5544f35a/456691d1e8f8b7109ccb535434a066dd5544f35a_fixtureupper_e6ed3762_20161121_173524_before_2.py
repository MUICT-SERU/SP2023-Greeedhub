from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from copy import deepcopy
import datetime
from decimal import Decimal
from future.utils import iteritems
import inspect
import json
import operator
import os

from sqlalchemy.inspection import inspect as sqlalchemy_inspect

from fixtureupper.model import ModelFixtureUpper


class SqlAlchemyModelFixtureUpper(ModelFixtureUpper):
    @classmethod
    def is_removeable_relation(cls, model, relation_prop):
        return bool(cls._get_relationship(model, relation_prop))

    @classmethod
    def get_fixture_to_json(cls, fixture):
        fields = vars(fixture)

        # Remove relation before writing to prevent circular json
        removed_relations = {k: v for k, v in iteritems(fields) if cls.is_removeable_relation(fixture, k)}
        for k, v in iteritems(removed_relations):
            # delattr removes completely if list, must copy
            removed_relations[k] = v[:] if isinstance(v, list) else v
            delattr(fixture, k)

        fields = deepcopy(fields)
        del fields['_sa_instance_state']

        # Delete null values from json
        remove = [k for k, v in iteritems(fields) if v is None]
        for k in remove:
            del fields[k]

        # Reset removed relations
        for k, v in iteritems(removed_relations):
            setattr(fixture, k, v)

        return cls.make_obj_json(fixture, fields)

    def get_model_attr_key(self, model=None):
        try:
            model = model or self.model
            # Get model class, not instance of model
            if not inspect.isclass(model):
                model = type(model)
            return sqlalchemy_inspect(model).primary_key[0].name
        except:
            return None

    @classmethod
    def get_relationships(cls, fixture=None):
        model = type(fixture) if fixture else cls.model
        return sqlalchemy_inspect(model).relationships

    @classmethod
    def _get_relationship(cls, fixture, relation_prop):
        return cls.get_relationships(fixture=fixture).get(relation_prop)

    def _set_relation_ids(self, fixture, related_fixture, relation_prop):
        if not related_fixture:
            return

        # set fixture's (i.e. Article)
        # foreign_key (i.e. main_author_id)
        # to primary_key of related_fixture (i.e. Author's author_id)
        relationship = self._get_relationship(fixture, relation_prop)
        if not relationship:
            return

        local_columns = list(relationship.local_columns)[0]

        # Only set keys if it's a foreign key of the model
        if local_columns.foreign_keys:
            foreign_key = local_columns.key
            related_model_pk = list(local_columns.foreign_keys)[0].column.key
            setattr(fixture, foreign_key, getattr(related_fixture, related_model_pk))

    def set_relation(self, fixture, related_fixtures, relation_prop):
        # Set fixture relation, backref's automatically made by sqlAlchemy
        setattr(fixture, relation_prop, related_fixtures)
        _property = getattr(type(fixture), relation_prop).property
        back_relation = _property.backref or _property.back_populates

        if not isinstance(related_fixtures, list):
            related_fixtures = [related_fixtures]
        for r in related_fixtures:
            self._set_relation_ids(fixture, r, relation_prop)
            self._set_relation_ids(r, fixture, back_relation)
