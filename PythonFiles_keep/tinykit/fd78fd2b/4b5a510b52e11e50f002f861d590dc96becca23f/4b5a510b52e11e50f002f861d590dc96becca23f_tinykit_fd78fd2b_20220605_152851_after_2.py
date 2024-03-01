def test_database_init():
    from tinykit import Database
    from tinydb.storages import MemoryStorage

    db = Database(storage=MemoryStorage)
    assert db._conn is not None
