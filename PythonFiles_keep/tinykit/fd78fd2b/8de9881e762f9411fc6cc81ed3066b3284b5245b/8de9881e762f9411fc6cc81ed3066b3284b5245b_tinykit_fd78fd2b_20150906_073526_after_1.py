from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import time
from datetime import datetime

from jsonmodels import fields

from timo.db import Database
from timo.models import Model


class TestingModel(Model):
    __tablename__ = "testing"

    name = fields.StringField()
    key = fields.StringField()
    created_at = fields.FloatField()

    # this attribute wont be saved because it's not a field
    address = "this attribute will not be saved"

    @property
    def location(self):
        return "Earth"

    def created_at_datetime(self):
        return datetime.fromtimestamp(self.created_at).isoformat()


def main():
    _, path = tempfile.mkstemp(suffix=".json")
    db = Database(path)

    model = TestingModel()
    model.name = "original"
    model.key = "test"
    model.created_at = time.time()

    table = db.table(model.__tablename__)
    with db.transaction(table) as tr:
        tr.insert(model.to_struct())
        model.name = "random"
        tr.update(model.to_struct(), db.where("key") == model.key)

    print(table.all())

    # create model from table's data
    row = table.get(db.where("key") == "test")
    new_model = TestingModel(**row)

    print(new_model.name)
    print(new_model.key)
    print(new_model.created_at)
    print(new_model.address)
    print(new_model.location)
    print(new_model.created_at_datetime())

    # cleanup
    os.unlink(path)


if __name__ == "__main__":
    main()
