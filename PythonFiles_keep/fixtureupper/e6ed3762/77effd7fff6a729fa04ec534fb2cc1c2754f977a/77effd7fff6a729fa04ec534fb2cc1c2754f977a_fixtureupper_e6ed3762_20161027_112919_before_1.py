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
from random import Random
from six import with_metaclass

from sqlalchemy.inspection import inspect as sqlalchemy_inspect


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
