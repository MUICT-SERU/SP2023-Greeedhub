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
        cls._UPPER_KEY = cls.get_upper_class_key()
        if cls._UPPER_KEY:
            cls._upper_classes[cls._UPPER_KEY] = cls
        super(UpperWatcher, cls).__init__(name, bases, clsdict)


class BaseFixtureUpper(with_metaclass(UpperWatcher, object)):
    _upper_classes = {}
    upper_aliases = {}

    def __init__(self, start_id=1, seed=None, upper_instances=None, **kwargs):
        self.start_id = start_id
        self.seed = seed

        self.fixtures = []
        self.defaults = getattr(self, 'defaults', {})
        self.seed_random()

        if upper_instances is None:
            upper_instances = {}

        self.upper_instances = upper_instances

        # Save most recent instance of upper
        # to upper map
        if getattr(self, '_UPPER_KEY', None):
            self.upper_instances[self._UPPER_KEY] = self

    @classmethod
    def get_upper_class_key(cls):
        # Don't register Base Fixture Upper Classes
        if cls.__name__ == 'BaseFixtureUpper':
            return None

        key = cls.__name__
        if key in cls._upper_classes:
            raise Exception('Fixture Upper with name %s exists, use another name' % key)
        return key

    def get_all_fixtures(self):
        list_of_lists = [
            instance.fixtures
            for key, instance
            in iteritems(self.upper_instances)
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
        key = self.upper_aliases.get(key, key)

        if key not in self.upper_instances:
            kwargs['upper_instances'] = self.upper_instances

            for kw in self.get_passed_kwarg_keys():
                if not kwargs.get(kw):
                    kwargs[kw] = getattr(self, kw)

            self._upper_classes[key](**kwargs)
        return self.upper_instances[key]

    def randint(self, *args):
        return self.random.randint(*args)

    def override_defaults(self, defaults):
        # Make sure global class defaults are not overridden
        self.defaults = dict(deepcopy(self.defaults), **defaults)

    def reset_defaults(self):
        self.defaults = self.__class__.defaults

    def generate(self, **kwargs):
        raise NotImplementedError
