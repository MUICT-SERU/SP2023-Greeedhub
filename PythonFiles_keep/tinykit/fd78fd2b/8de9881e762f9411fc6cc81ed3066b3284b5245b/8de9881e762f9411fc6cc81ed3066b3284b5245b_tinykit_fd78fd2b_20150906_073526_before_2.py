from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def test_model_without_tablename():
    from timo.models import BaseModel

    class TestModel(BaseModel):
        pass

    model = TestModel()
    assert model.__tablename__ == "testmodel"


def test_model_with_tablename():
    from timo.models import BaseModel

    class TestModel(BaseModel):
        __tablename__ = "mytable"

    model = TestModel()
    assert model.__tablename__ == "mytable"
