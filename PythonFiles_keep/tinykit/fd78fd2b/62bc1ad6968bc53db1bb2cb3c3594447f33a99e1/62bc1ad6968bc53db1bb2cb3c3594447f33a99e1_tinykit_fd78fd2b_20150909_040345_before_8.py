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
        self.table = self._conn.table
        self.where = where
        self.transaction = transaction

    def __repr__(self):
        return "<{}: storage={}>".format(
            self.__class__.__name__,
            self._conn._storage.__class__.__name__,
        )
