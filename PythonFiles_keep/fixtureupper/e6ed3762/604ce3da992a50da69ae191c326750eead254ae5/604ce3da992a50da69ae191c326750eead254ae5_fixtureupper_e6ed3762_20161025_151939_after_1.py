from copy import deepcopy
import datetime
from decimal import Decimal
from future.utils import iteritems
import inspect
import json
import operator
import os
from random import Random
from six import with_metaclass

from sqlalchemy.inspection import inspect as sqlalchemy_inspect

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


# Watch when new FixtureUppers are created and register them to the class's global dictionary
class UpperWatcher(type):
    def __init__(cls, name, bases, clsdict):
        cls._GENERATOR_KEY = cls.get_generator_class_key()
        if cls._GENERATOR_KEY:
            cls._generator_classes[cls._GENERATOR_KEY] = cls
        super(UpperWatcher, cls).__init__(name, bases, clsdict)


class BaseFixtureUpper(with_metaclass(UpperWatcher, object)):
    _generator_classes = {}
    generator_aliases = {}

    def __init__(self, start_id=1, seed=None, generator_instances=None, **kwargs):
        self.start_id = start_id
        self.seed = seed

        self.fixtures = []
        self.defaults = getattr(self, 'defaults', {})
        self.seed_random()

        if generator_instances is None:
            generator_instances = {}

        self.generator_instances = generator_instances

        # Save most recent instance of generator
        # to generator map
        if getattr(self, '_GENERATOR_KEY', None):
            self.generator_instances[self._GENERATOR_KEY] = self

    @classmethod
    def get_generator_class_key(cls):
        # Don't register Base Fixture Upper Classes
        if cls.__name__ == 'BaseFixtureUpper':
            return None

        key = cls.__name__
        if key in cls._generator_classes:
            raise Exception('Fixture Upper with name %s exists, use another name' % key)
        return key

    def get_all_fixtures(self):
        list_of_lists = [
            instance.fixtures
            for key, instance
            in iteritems(self.generator_instances)
        ]
        return [fixture for fixture_list in list_of_lists for fixture in fixture_list]

    def seed_random(self, seed=None):
        seed = seed or self.seed
        self.random = Random()
        self.random.seed(seed)

    def get_passed_kwarg_keys(self):
        return ['start_id', 'seed']

    def get_upper(self, key, **kwargs):
        # Get alias of key if available
        key = self.generator_aliases.get(key, key)

        if key not in self.generator_instances:
            kwargs['generator_instances'] = self.generator_instances

            for kw in self.get_passed_kwarg_keys():
                if not kwargs.get(kw):
                    kwargs[kw] = getattr(self, kw)

            self._generator_classes[key](**kwargs)
        return self.generator_instances[key]

    def randint(self, *args):
        return self.random.randint(*args)

    def override_defaults(self, defaults):
        # Make sure global class defaults are not overridden
        self.defaults = dict(deepcopy(self.defaults), **defaults)

    def reset_defaults(self):
        self.defaults = self.__class__.defaults

    def generate(self, **kwargs):
        raise NotImplementedError


class _ModelFixtureUpper(BaseFixtureUpper):
    required_attributes = []

    def __init__(self, *args, **kwargs):
        super(_ModelFixtureUpper, self).__init__(*args, **kwargs)
        self._model_id = self.start_id

        if getattr(self, 'model', None):
            # Load the primary key of model into fixture upper
            self.attr_key = self._get_model_attr_key()
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
        def _removeable_relation(model, relation_prop):
            return bool(cls._get_relationship(model, relation_prop))

        fields = vars(fixture)

        # Remove relation before writing to prevent circular json
        removed_relations = {k: v for k, v in iteritems(fields) if _removeable_relation(fixture, k)}
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

    def _get_model_attr_key(self, model=None):
        try:
            model = model or self.model
            # Get model class, not instance of model
            if not inspect.isclass(model):
                model = type(model)
            return sqlalchemy_inspect(model).primary_key[0].name
        except:
            return None

    def get_model_id(self, inc=True):
        """
        Returns id for model
        By default increments value of the id by 1
        """

        v = getattr(self, self.attr_key)
        if inc:
            setattr(self, self.attr_key, v + 1)
        return v

    @classmethod
    def _get_relationship(cls, model, relation_prop):
        return sqlalchemy_inspect(type(model)).relationships.get(relation_prop)

    def set_relations(self, fixture, relations):
        # set model's (i.e. Article)
        # foreign_key (i.e. main_author_id)
        # to primary_key of related_model (i.e. Author's author_id)
        def _set_relation_ids(model, related_model, relation_prop):
            relationship = self._get_relationship(model, relation_prop)
            if not relationship:
                return

            local_columns = list(relationship.local_columns)[0]

            # Only set keys if it's a foreign key of the model
            if local_columns.foreign_keys:
                foreign_key = local_columns.key
                related_model_pk = list(local_columns.foreign_keys)[0].column.key
                setattr(model, foreign_key, getattr(related_model, related_model_pk))

        for k, relation in iteritems(relations):
            # Set fixture relation, backref's automatically made by sqlAlchemy
            setattr(fixture, k, relation)
            _property = getattr(type(fixture), k).property
            back_relation = _property.backref or _property.back_populates

            if not isinstance(relation, list):
                relation = [relation]
            for r in relation:
                _set_relation_ids(fixture, r, k)
                _set_relation_ids(r, fixture, back_relation)

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

        relationships = sqlalchemy_inspect(self.model).relationships
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


def UpperRegister(upper_type):
    if upper_type == 'Base':
        return type('BaseFixtureUpper', (BaseFixtureUpper,), {
            '_generator_classes': {},
        })
    elif upper_type == 'Model':
        return type('ModelFixtureUpper', (_ModelFixtureUpper,), {
            '_generator_classes': {},
        })
    raise RuntimeError
