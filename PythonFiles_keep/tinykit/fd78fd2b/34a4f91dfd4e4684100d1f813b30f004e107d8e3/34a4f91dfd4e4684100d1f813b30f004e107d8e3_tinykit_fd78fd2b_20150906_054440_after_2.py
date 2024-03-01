from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tinydb import TinyDB
from tinydb import where
from tinyrecord import transaction


def resolve_tablename(maybe_model):
    tablename = getattr(maybe_model, "__tablename__", None)
    if tablename is None:
        tablename = maybe_model
    return tablename


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

    def table(self, maybe_model, smart_cache=False, **kwargs):
        """A shortcut to ``tinydb.TinyDB.table`` method.

        A notable difference with the original method is the ability
        to use plain string name or from model's ``__tablename__``
        attribute.

        An example of using plain string::

            table = db.table("testing")

        If we have a model::

            from timo.models import BaseModel

            class Testing(BaseModel):
                __tablename__ = "testing"

            table = db.table(Testing)

        Both approaches return a reference to "testing" table
        in database.
        """
        name = resolve_tablename(maybe_model)
        return self._conn.table(name, smart_cache, **kwargs)

    def where(self, key):
        """A shortcut to ``tinydb.where`` method.
        """
        return where(key)
