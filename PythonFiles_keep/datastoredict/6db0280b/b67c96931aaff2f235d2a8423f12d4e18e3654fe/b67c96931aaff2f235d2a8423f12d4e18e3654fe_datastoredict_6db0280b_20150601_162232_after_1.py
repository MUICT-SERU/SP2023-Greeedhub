"""
A durabledict implementation for AppEngine.
"""

from google.appengine.api import memcache
from google.appengine.ext import ndb

from durabledict.base import DurableDict
from durabledict.encoding import NoOpEncoding


class DatastoreDictAncestorModel(ndb.Model):
    """
    A common ancestor for all DatastoreDict entities.
    Forces strong read consistency across all instances.
    """

    @classmethod
    def generate_key(cls, child_cls):
        """
        Build a key.
        """
        key_name = '_%s-%s_' % ('ancestor', child_cls.__name__)
        return ndb.Key(cls, key_name, namespace='')


def build_key(cls, key):
    """
    Build a key.
    """
    return ndb.Key(DatastoreDictAncestorModel,
                   DatastoreDictAncestorModel.generate_key(cls).string_id(),
                   cls, key.lower(),
                   namespace='')


@ndb.transactional
def get_all(cls):
    """
    Return all instances of the specified class.
    """
    return cls.query(
        ancestor=DatastoreDictAncestorModel.generate_key(cls)).fetch()


@ndb.transactional
def get(cls, key):
    """
    Get an entity by key
    """
    return build_key(cls, key).get()


@ndb.transactional
def get_or_create(cls, key, value=None):
    """
    Return a key or create the key with a default value.
    """
    key = build_key(cls, key)

    instance = key.get()
    if instance:
        return instance, False

    instance = cls(key=key, value=value)
    instance.put()

    return instance, True


@ndb.transactional
def delete(cls, key):
    """
    Get an entity by key
    """
    key = build_key(cls, key)
    return key.delete()


class DatastoreDict(DurableDict):
    """
    Dictionary-style access to a model. Populates a local in-memory
    cache to avoid multiple hits to the database.
    """

    def __init__(self, model,
                 cache=memcache,
                 value_col='value',
                 cache_key=None):

        if not model:
            raise ValueError('model is required.')

        self.model = model
        self.value_col = value_col
        self.cache = cache
        self.cache_key = cache_key or "%s-%s" % (model.__name__,
                                                 'last_updated')

        super(DatastoreDict, self).__init__(encoding=NoOpEncoding)

    def persist(self, key, val):
        """
        Store val at key in the datastore.
        """
        instance, created = get_or_create(self.model, key, val)

        if not created and instance.value != val:
            setattr(instance, self.value_col, val)
            instance.put()

        self.touch_last_updated()

    def depersist(self, key):
        """
        Remove the key from the datastore.
        """
        delete(self.model, key)
        self.touch_last_updated()

    def durables(self):
        """
        Return all keys and values.
        """
        models = get_all(self.model)
        return dict((model.key.id(), getattr(model, self.value_col))
                    for model in models)

    def _setdefault(self, key, default=None):
        """
        If key is in the dictionary, return its value.
        If not, insert key with a value of default and
        return default. default defaults to None.
        """
        instance, created = get_or_create(self.model, key, default)

        if created:
            self.touch_last_updated()

        return getattr(instance, self.value_col)

    def _pop(self, key, default=None):
        """
        If key is in the dictionary, remove it and return its value,
        else return default. If default is not given and key is not
        in the dictionary, a KeyError is raised.
        """
        instance = get(self.model, key)
        if instance:
            value = getattr(instance, self.value_col)
            delete(self.model, key)
            self.touch_last_updated()
            return value
        else:
            if default is not None:
                return default
            else:
                raise KeyError

    def last_updated(self):
        """
        Return the last updated stamp.
        """
        cache_val = self.cache.get(self.cache_key)
        if cache_val:
            return cache_val
        else:
            self.touch_last_updated()
            return 1

    def touch_last_updated(self):
        """
        Increment the last updated stamp. If the cache key does not exist,
        use the last known value.
        """
        self.cache.incr(self.cache_key, initial_value=self.last_synced)
