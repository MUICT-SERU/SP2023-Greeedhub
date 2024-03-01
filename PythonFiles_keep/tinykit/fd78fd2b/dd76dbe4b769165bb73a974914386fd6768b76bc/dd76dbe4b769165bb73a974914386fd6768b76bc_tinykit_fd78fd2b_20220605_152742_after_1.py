import os
import tempfile
import time

from tinykit import Database


def main():
    _, path = tempfile.mkstemp(suffix=".json")
    db = Database(path)

    table = db.table("testing")
    with db.transaction(table) as tr:
        tr.insert({"created_at": time.time(), "key": "test"})
        tr.update({"name": "random"}, db.where("key") == "test")

    print(table.all())

    # cleanup
    os.unlink(path)


if __name__ == "__main__":
    main()
