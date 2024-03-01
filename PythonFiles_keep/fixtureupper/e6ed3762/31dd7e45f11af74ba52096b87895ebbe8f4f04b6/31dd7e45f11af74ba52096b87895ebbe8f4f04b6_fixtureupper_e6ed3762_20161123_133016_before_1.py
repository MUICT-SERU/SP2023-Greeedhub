from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from collections import defaultdict
from copy import deepcopy
import datetime
from decimal import Decimal
from future.utils import iteritems
import inspect
import json
import os
from past.builtins import basestring

from fixtureupper.base import BaseFixtureUpper


class ModelFixtureUpper(BaseFixtureUpper):
    required_attributes = []
    generated_field_order = []

    def __init__(self, *args, **kwargs):
        super(ModelFixtureUpper, self).__init__(*args, **kwargs)
        self._model_id = self.start_id

        if getattr(self, 'model', None):
            # Load the primary key of model into fixture upper
            self.attr_key = self.get_model_attr_key()
            setattr(self, self.attr_key, self.start_id)

    @classmethod
    def get_upper_class_key(cls):
        try:
            return cls.model.__name__
        except:
            return None

    @classmethod
    def make_obj_json(cls, obj, str_obj, super_class=None):
        obj_json = {
            '__class__': type(obj).__name__,
            '__value__': str_obj,
        }

        if super_class:
            obj_json['__super_class__'] = super_class

        return obj_json

    @classmethod
    def dynamic_import_and_eval(cls, import_statement, eval_str):
        # FIXME Runtime imports and evals...ew.
        # noinspection PyUnresolvedReferences
        exec(import_statement)
        return eval(eval_str)

    @classmethod
    def get_python_objects_for_json(cls):
        pos = {
            datetime.datetime: {
                'to_json': lambda obj: cls.make_obj_json(obj, repr(obj)),
                'from_json': lambda obj: cls.dynamic_import_and_eval('import datetime', obj['__value__']),
            },
            Decimal: {
                'to_json': lambda obj: cls.make_obj_json(obj, repr(obj)),
                'from_json': lambda obj: cls.dynamic_import_and_eval('from decimal import Decimal', obj['__value__']),
            },
        }

        def get_from_json(model):
            return lambda obj: model(**obj['__value__'])

        for name, upper_class in iteritems(cls._upper_classes):
            if getattr(upper_class, 'model', None):
                pos[upper_class.model] = {
                    'to_json': lambda obj: cls.get_fixture_to_json(obj),
                    'from_json': get_from_json(upper_class.model),
                }

        return pos

    @classmethod
    def get_fixture_to_dict(cls, fixture):
        raise NotImplementedError

    @classmethod
    def get_fixture_to_json(cls, fixture):
        fields = cls.get_fixture_to_dict(fixture)
        return cls.make_obj_json(fixture, fields)

    def get_current_fixtures_json(self):
        return self.get_fixtures_json(self.get_all_fixtures())

    @classmethod
    def sorted_models_key(cls, model_name):
        # FIXME: sort working depends on number of fixture models being less than 10000
        try:
            order_num = cls.all_fixtures_order.index(model_name)
        except:
            order_num = len(cls.all_fixtures_order)
        return '%04d_%s' % (order_num, model_name)

    @classmethod
    def sorted_fixtures_key(cls, f):
        return cls.sorted_models_key(type(f).__name__)

    # Transform python object into json compatible representation
    @classmethod
    def get_default_to_json(cls):
        python_objects = cls.get_python_objects_for_json()

        def _to_json(obj):
            # Check if type is directly in python_objects
            transforms = python_objects.get(type(obj))
            if transforms:
                return transforms['to_json'](obj)

            # Else check if superclass is in python_objects
            for python_object, transforms in iteritems(python_objects):
                if isinstance(obj, python_object):
                    return transforms['to_json'](obj)
            return obj

        return _to_json

    @classmethod
    def get_fixtures_json(cls, fixtures):
        out = sorted(fixtures or [], key=cls.sorted_fixtures_key)
        return json.dumps(out, indent=4, default=cls.get_default_to_json(), sort_keys=True)

    @classmethod
    def print_fixtures(cls, *args, **kwargs):
        return cls.print_json_fixtures(*args, **kwargs)

    @classmethod
    def _print_fixtures(cls, savedir, fname, data):
        """Function to print model fixtures into generated file"""
        if not os.path.exists(savedir):
            os.makedirs(savedir)

        with open(os.path.join(savedir, fname), 'w') as fout:
            fout.write(data)

    @classmethod
    def print_json_fixtures(cls, savedir, fname, fixtures):
        return cls._print_fixtures(savedir, fname, cls.get_fixtures_json(fixtures))

    @classmethod
    def print_sql_fixtures(cls, savedir, fname, fixtures):
        return cls._print_fixtures(savedir, fname, cls.stats_fixtures_to_sql(fixtures))

    @classmethod
    def sort_fixtures_by_model(cls, fixtures):
        def _get_default_dict():
            return {
                'keys': set(),
                'values': [],
            }

        _fixtures = defaultdict(_get_default_dict)

        for f in fixtures:
            table = _fixtures[type(f).__name__]
            table['keys'].update(cls.get_fixture_to_dict(f).keys())
            table['values'].append(f)

        return _fixtures

    @classmethod
    def to_sql(cls, val):
        if isinstance(val, datetime.datetime):
            return 'TIMESTAMP \'%s\'' % str(val)
        elif isinstance(val, basestring):
            return "'%s'" % val
        elif val is None:
            return 'NULL'
        return json.dumps(val)

    @classmethod
    def get_table_name_from_fixture(cls, f):
        raise NotImplementedError

    @classmethod
    def stats_fixtures_to_sql(cls, fixtures):
        fixtures = cls.sort_fixtures_by_model(fixtures)
        statement_groups = []

        def _sort_key(_tuple):
            return cls.sorted_models_key(_tuple[0])

        for model_name, table_dict in sorted(iteritems(fixtures), key=_sort_key):
            fixture_list = table_dict['values']
            if not fixture_list:
                continue

            table_name = cls.get_table_name_from_fixture(fixture_list[0])
            data_keys = sorted(list(table_dict['keys']))
            header = 'INSERT INTO %s (%s) VALUES' % (table_name, ', '.join(data_keys))

            statements = [
                '(%s)' % ', '.join(cls.to_sql(getattr(f, key)) for key in data_keys)
                for f in fixture_list
            ]
            statement_groups.append('%s\n%s;\n' % (header, ',\n'.join(statements)))

        return '\n'.join(statement_groups)

    @classmethod
    def get_fixtures_from_json(cls, json_str):
        python_objects = cls.get_python_objects_for_json()
        po_by_name = {po.__name__: transforms for po, transforms in iteritems(python_objects)}

        # Transform json representation of python object to python object
        # TODO Add ability to get using super_classes
        def from_json(obj):
            if '__class__' in obj:
                transforms = po_by_name.get(obj['__class__'])
                if transforms:
                    return transforms['from_json'](obj)
            return obj

        return json.loads(json_str, object_hook=from_json)

    @classmethod
    def read_fixtures_json(cls, fname):
        """Read json file to get fixture data"""
        if not os.path.exists(fname):
            raise RuntimeError

        with open(fname, 'r') as data_file:
            return cls.get_fixtures_from_json(data_file.read())

    def get_model_attr_key(self, model=None):
        raise NotImplementedError

    def get_model_id(self, inc=True):
        """
        Returns id for model
        By default increments value of the id by 1
        """

        v = getattr(self, self.attr_key)
        if inc:
            setattr(self, self.attr_key, v + 1)
        return v

    def set_relation(fixture, related_fixtures, relation_prop):
        raise NotImplementedError

    def _is_generator_function(self, obj):
        return callable(obj)

    def _call_generator_function(self, fn, fixture, key):
        return fn(self, fixture, key)

    def set_relations(self, fixture, relations):
        generator_relations = {}

        for k, related_fixtures in iteritems(relations):
            # if relation is a generator function, skip to generate later
            if self._is_generator_function(related_fixtures):
                generator_relations[k] = related_fixtures
            else:
               self.set_relation(fixture, related_fixtures, k)

        for k, related_fixtures in self.sorted_by_generated_order(generator_relations):
            # generate relations and pass in as relation
            generated = self._call_generator_function(related_fixtures, fixture, k)
            self.set_relation(fixture, generated, k)

    @classmethod
    def get_relationships(cls):
        raise NotImplementedError

    def sorted_by_generated_order(self, data):
        def _sort(_tuple):
            try:
                return self.generated_field_order.index(_tuple[0])
            except:
                return len(self.generated_field_order)

        return sorted(iteritems(data), key=_sort)

    def update_fixtures_with_data(self, data, fixtures=None):
        fixtures = fixtures or self.fixtures
        for i, d in enumerate(data):
            for key, val in iteritems(d):
                setattr(fixtures[i], key, val)

    def single_fixup(self, data=None, **kwargs):
        data = data if isinstance(data, dict) else {}
        relations = {}

        # Get model values through mix of default values and passed in values
        model_values = dict(self.defaults, **data)

        # Generate model's primary key value if it has a primary key
        if self.attr_key and not model_values.get(self.attr_key):
            model_values[self.attr_key] = self.get_model_id()

        generator_functions = {}

        relationships = self.get_relationships()
        for key, value in iteritems(model_values):
            # If model values are relations, move them to relations dict
            if relationships.get(key):
                relations[key] = value

            # Else if model values are generator functions, move them away from model_values
            elif self._is_generator_function(value):
                generator_functions[key] = value

        for key in frozenset(generator_functions.keys()).union(frozenset(relations.keys())):
            model_values.pop(key, None)

        # Set fixture's attributes with model_values dict and relation dict
        fixture = self.model(**model_values)
        self.set_relations(fixture, relations)

        # Call generator functions after initial values/relations have been set
        for key, fn in self.sorted_by_generated_order(generator_functions):
            generated = self._call_generator_function(fn, fixture, key)
            setattr(fixture, key, generated)

        # Check to make sure required attibutes have been set
        for attr in self.required_attributes:
            if getattr(fixture, attr, None) is None:
                raise Exception('%s is not set for %s' % (attr, str(fixture)))

        self.fixtures.append(fixture)
        return fixture

    def fixup(self, data=None, **kwargs):
        if isinstance(data, list):
            fixtures = []
            for d in data:
                fixtures.append(self.single_fixup(data=d, **kwargs))
            return fixtures
        else:
            return self.single_fixup(data=data, **kwargs)
