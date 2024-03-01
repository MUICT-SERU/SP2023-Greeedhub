from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tinydb import TinyDB
from tinydb import where
from tinyrecord import transaction


class Database(object):
    def __init__(self, *args, **kwargs):
        self._conn = TinyDB(*args, **kwargs)

    def transaction(self, table):
        """Create an atomic transaction for the given *table*.

        Typical usage::

            from timo.db import Database

            db = Database("/path/to/database.json")
            table = db.table("users")
            with db.transaction(table) as tr:
                tr.insert({"name": "test"})

        :param table: An instance of ``tinydb.database.Table`` object.
        :returns: An instance of ``tinyrecord.transaction.transaction``
                  object.
        """
        return transaction(table)

    def table(self, name, smart_cache=False, **kwargs):
        return self._conn.table(name, smart_cache, **kwargs)

    def where(self, key):
        return where(key)
