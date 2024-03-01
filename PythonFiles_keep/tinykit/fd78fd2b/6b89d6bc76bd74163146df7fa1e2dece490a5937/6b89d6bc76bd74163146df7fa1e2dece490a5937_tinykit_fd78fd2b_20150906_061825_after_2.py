from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import time

from jsonmodels import fields

from timo.db import Database
from timo.models import BaseModel


class TestingModel(BaseModel):
    __tablename__ = "testing"

    name = fields.StringField()
    key = fields.StringField()
    created_at = fields.FloatField()


def main():
    _, path = tempfile.mkstemp(suffix=".json")
    db = Database(path)

    model = TestingModel()
    model.name = "original"
    model.key = "test"
    model.created_at = time.time()

    table = db.table(model)
    with db.transaction(table) as tr:
        tr.insert(model.to_struct())
        tr.update({"name": "random"}, db.where("key") == model.key)

    print(table.all())

    # cleanup
    os.unlink(path)


if __name__ == "__main__":
    main()
