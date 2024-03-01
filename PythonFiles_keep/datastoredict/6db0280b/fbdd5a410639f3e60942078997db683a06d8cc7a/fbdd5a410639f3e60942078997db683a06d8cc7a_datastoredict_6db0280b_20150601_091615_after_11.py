import unittest

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from datastoredict import DatastoreDict
from datastoredict.datastoredict import build_key


class GaeTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()


class DatastoreDictModel(ndb.Model):
    """
    A datastore model for storing durabledict data.
    """
    value = ndb.PickleProperty()


class DatastoreDictInitTests(GaeTestCase):

    def test_init_new_dict_copies_existing_values(self):
        new_dict = DatastoreDict(model=DatastoreDictModel)
        new_dict.persist('key', 'value')

        new_dict = DatastoreDict(model=DatastoreDictModel)
        self.assertEqual(new_dict['key'], 'value')

    def test_init_new_dict_does_not_invalidate_cache(self):
        new_dict = DatastoreDict(model=DatastoreDictModel)
        new_dict.persist('key', 'value')
        old_cache_val = memcache.get(new_dict.cache_key)

        new_dict = DatastoreDict(model=DatastoreDictModel)
        new_cache_val = memcache.get(new_dict.cache_key)
        self.assertEqual(old_cache_val, new_cache_val)

        self.assertEquals(new_dict.last_synced, old_cache_val)
        self.assertEquals(new_dict.last_synced, new_cache_val)


class DatastoreDictPersistTests(GaeTestCase):
    def setUp(self):
        super(DatastoreDictPersistTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)

    def test_creates_datastore_entity(self):
        self.datastore_dict.persist('key', 'value')
        entity = build_key(DatastoreDictModel, 'key').get()
        self.assertEqual(entity.key.id(), 'key')
        self.assertEqual(entity.value, 'value')

    def test_updates_existing_entity(self):
        self.datastore_dict.persist('key', 'value')
        self.datastore_dict.persist('key', 'new_value')
        entity = build_key(DatastoreDictModel, 'key').get()
        self.assertEqual(entity.key.id(), 'key')
        self.assertEqual(entity.value, 'new_value')

    def test_updates_cache_value(self):
        cache_val = self.datastore_dict.last_updated()
        self.assertEqual(cache_val, 1)

        self.datastore_dict.persist('key', 'value')

        cache_val = self.datastore_dict.last_updated()
        self.assertEqual(cache_val, 2)


class DatastoreDictDepersistTests(GaeTestCase):
    def setUp(self):
        super(DatastoreDictDepersistTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)

    def test_does_not_raise_when_missing_key(self):
        self.datastore_dict.depersist('key')

    def test_removes_key(self):
        self.datastore_dict.persist('key', 'value')
        self.datastore_dict.depersist('key')
        entity = build_key(DatastoreDictModel, 'key').get()
        self.assertIsNone(entity)

    def test_updates_cache_value(self):
        self.datastore_dict.persist('key', 'value')
        old_cache_val = memcache.get(self.datastore_dict.cache_key)

        self.datastore_dict.depersist('key')

        new_cache_val = memcache.get(self.datastore_dict.cache_key)
        self.assertEqual(new_cache_val, old_cache_val + 1)


class DurablesTests(GaeTestCase):

    def setUp(self):
        super(DurablesTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)

    def test_returns_empty_dict_if_no_entities(self):
        self.assertEqual(self.datastore_dict.durables(), {})

    def test_returns_all_entities(self):
        self.datastore_dict.persist('key1', 'value')
        self.datastore_dict.persist('key2', 'value')
        self.datastore_dict.persist('key3', 'value')

        self.assertEqual(self.datastore_dict.durables(),
                         {'key1': 'value',
                          'key2': 'value',
                          'key3': 'value'})


class SetDefaultTests(GaeTestCase):

    def setUp(self):
        super(SetDefaultTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)

    def test_does_not_touch_last_updated_if_key_exists(self):
        self.datastore_dict.persist('key', 'value')

        old_cache_val = self.datastore_dict.last_updated()

        self.datastore_dict._setdefault('key', 'new_value')

        new_cache_val = self.datastore_dict.last_updated()
        self.assertEqual(old_cache_val, new_cache_val)

    def test_updates_last_updated_on_create(self):
        old_cache_val = self.datastore_dict.last_updated()

        self.datastore_dict._setdefault('key', 'value')

        new_cache_val = memcache.get(self.datastore_dict.cache_key)
        self.assertEqual(old_cache_val + 1, new_cache_val)

    def test_creates_new_entity(self):
        self.datastore_dict._setdefault('key', 'value')

        entity = build_key(DatastoreDictModel, 'key').get()

        self.assertEqual(entity.key.id(), 'key')
        self.assertEqual(entity.value, 'value')


class PopTests(GaeTestCase):

    def setUp(self):
        super(PopTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)
        self.datastore_dict.persist('key', 'value')

    def test_KeyError_on_missing_key(self):
        with self.assertRaises(KeyError):
            self.datastore_dict._pop('missing-key')

    def test_returns_default_on_missing_key(self):
        value = self.datastore_dict._pop('missing-key', default='value')
        self.assertEquals(value, 'value')

    def test_returns_popped_value(self):
        value = self.datastore_dict._pop('key')
        self.assertEquals(value, 'value')

    def test_updates_last_updated_when_popped(self):
        old_cache_val = memcache.get(self.datastore_dict.cache_key)

        self.datastore_dict._pop('key')

        new_cache_val = memcache.get(self.datastore_dict.cache_key)
        self.assertEqual(old_cache_val + 1, new_cache_val)

    def test_removes_popped_value_from_dict(self):
        self.datastore_dict._pop('key')
        entity = build_key(DatastoreDictModel, 'key').get()
        self.assertIsNone(entity)
        self.assertEquals(self.datastore_dict.durables(), {})


class LastUpdatedTests(GaeTestCase):

    def setUp(self):
        super(LastUpdatedTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)

    def test_returns_initial_value_if_no_updates(self):
        value = self.datastore_dict.last_updated()
        self.assertEquals(value, 1)

    def test_returns_intial_value_if_no_cache_key(self):
        memcache.delete(self.datastore_dict.cache_key)
        value = self.datastore_dict.last_updated()
        self.assertEquals(value, 1)


class TouchLastUpdatedTests(GaeTestCase):

    def setUp(self):
        super(TouchLastUpdatedTests, self).setUp()
        self.datastore_dict = DatastoreDict(model=DatastoreDictModel)

    def test_increments_last_updated(self):
        old_value = self.datastore_dict.last_updated()
        self.datastore_dict.touch_last_updated()
        new_value = self.datastore_dict.last_updated()
        self.assertEquals(new_value, old_value + 1)

    def test_uses_last_synced_if_no_cache_key(self):
        old_value = self.datastore_dict.last_updated()
        memcache.delete(self.datastore_dict.cache_key)
        self.datastore_dict.touch_last_updated()
        new_value = self.datastore_dict.last_updated()
        self.assertEquals(new_value, old_value + 1)
