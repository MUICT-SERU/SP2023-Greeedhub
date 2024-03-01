from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import time

from timo import Database


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
