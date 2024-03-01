from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def test_database_init():
    from timo import Database
    from tinydb.storages import MemoryStorage

    db = Database(storage=MemoryStorage)
    assert db._conn.__class__.__name__ == "TinyDB"
