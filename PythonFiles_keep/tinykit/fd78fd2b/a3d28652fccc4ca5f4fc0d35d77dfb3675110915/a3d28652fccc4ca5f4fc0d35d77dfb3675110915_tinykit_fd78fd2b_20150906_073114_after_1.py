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
        """A shortcut to ``tinyrecord.transaction.transaction`` class.

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
        """A shortcut to ``tinydb.TinyDB.table`` method.
        """
        return self._conn.table(name, smart_cache, **kwargs)

    def where(self, key):
        """A shortcut to ``tinydb.where`` object.
        """
        return where(key)

    def __repr__(self):
        return "<{}: storage={}>".format(
            self.__class__.__name__,
            self._conn._storage.__class__.__name__,
        )
