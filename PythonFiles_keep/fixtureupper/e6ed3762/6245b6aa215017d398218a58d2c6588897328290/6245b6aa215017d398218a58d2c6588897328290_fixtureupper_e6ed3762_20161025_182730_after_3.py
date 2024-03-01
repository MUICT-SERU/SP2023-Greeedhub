from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from copy import deepcopy
import datetime
from decimal import Decimal
from future.utils import iteritems
import inspect
import json
import os

from fixtureupper.base import BaseFixtureUpper


def cmp_to_key(mycmp):
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K


class ModelFixtureUpper(BaseFixtureUpper):
    required_attributes = []

    def __init__(self, *args, **kwargs):
        super(ModelFixtureUpper, self).__init__(*args, **kwargs)
        self._model_id = self.start_id

        if getattr(self, 'model', None):
            # Load the primary key of model into fixture upper
            self.attr_key = self.get_model_attr_key()
            setattr(self, self.attr_key, self.start_id)

    @classmethod
    def get_generator_class_key(cls):
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

        for name, upper_class in iteritems(cls._generator_classes):
            if getattr(upper_class, 'model', None):
                pos[upper_class.model] = {
                    'to_json': lambda obj: cls.get_fixture_to_json(obj),
                    'from_json': get_from_json(upper_class.model),
                }

        return pos

    @classmethod
    def get_fixture_to_json(cls, fixture):
        raise NotImplementedError

    def get_current_fixtures_json(self):
        return self.get_fixtures_json(self.get_all_fixtures())

    @classmethod
    def get_fixtures_json(cls, fixtures):
        if not fixtures:
            raise RuntimeError

        python_objects = cls.get_python_objects_for_json()

        # Transform python object into json compatible representation
        def to_json(obj):
            # Check if type is directly in python_objects
            transforms = python_objects.get(type(obj))
            if transforms:
                return transforms['to_json'](obj)

            # Else check if superclass is in python_objects
            for python_object, transforms in iteritems(python_objects):
                if isinstance(obj, python_object):
                    return transforms['to_json'](obj)
            return obj

        # Sort output array by model name first
        out = [f for f in fixtures]

        def compare(f1, f2):
            n1 = type(f1).__name__
            n2 = type(f2).__name__

            if n1 > n2: return 1
            elif n1 < n2: return -1
            return 0

        out.sort(key=cmp_to_key(compare))

        return json.dumps(out, indent=4, default=to_json, sort_keys=True)

    @classmethod
    def print_fixtures(cls, savedir, fname, fixtures):
        """Function to print model fixtures into generated file"""
        if not os.path.exists(savedir):
            os.makedirs(savedir)

        with open('%s%s' % (savedir, fname), 'w') as fout:
            fout.write(cls.get_fixtures_json(fixtures))

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

    def set_relations(self, fixture, relations):
        raise NotImplementedError

    @classmethod
    def get_relationships(cls):
        raise NotImplementedError

    def update_fixtures_with_data(self, data, fixtures=None):
        fixtures = fixtures or self.fixtures
        for i, d in enumerate(data):
            for key, val in iteritems(d):
                setattr(fixtures[i], key, val)

    def _generate(self, data=None, **kwargs):
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
            elif callable(value):
                generator_functions[key] = value

        for key in frozenset(generator_functions.keys()).union(frozenset(relations.keys())):
            model_values.pop(key, None)

        # Set fixture's attributes with model_values dict and relation dict
        fixture = self.model(**model_values)
        self.set_relations(fixture, relations)

        # Call generator functions after initial values/relations have been set
        for key, fn in iteritems(generator_functions):
            setattr(fixture, key, fn(self, fixture))

        # Check to make sure required attibutes have been set
        for attr in self.required_attributes:
            if getattr(fixture, attr, None) is None:
                raise Exception('%s is not set for %s' % (attr, str(fixture)))

        self.fixtures.append(fixture)
        return fixture

    def generate(self, data=None, **kwargs):
        if isinstance(data, list):
            fixtures = []
            for d in data:
                fixtures.append(self._generate(data=d, **kwargs))
            return fixtures
        else:
            return self._generate(data=data, **kwargs)
