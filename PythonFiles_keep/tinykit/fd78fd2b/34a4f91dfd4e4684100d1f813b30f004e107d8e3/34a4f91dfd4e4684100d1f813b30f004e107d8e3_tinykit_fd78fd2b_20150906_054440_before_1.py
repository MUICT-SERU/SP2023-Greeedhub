from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from tinydb.storages import MemoryStorage


@pytest.fixture(scope="session")
def db():
    from timo.db import Database
    return Database(storage=MemoryStorage)


@pytest.fixture()
def table(db):
    return db.table("testing")


def test_database_init(db):
    assert db._conn.__class__.__name__ == "TinyDB"


def test_database_table(table):
    assert table.__class__.__name__ == "Table"


def test_database_transaction(db, table):
    assert db.transaction(table).__class__.__name__ == "transaction"


def test_database_where(db, table):
    table.insert({"id": 1})
    assert table.search(db.where("id") == 1)
