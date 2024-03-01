from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonmodels.models
from six import add_metaclass


class TablenameMeta(type):
    def __new__(cls, name, parents, args, **kwargs):
        if "__tablename__" not in args:
            args["__tablename__"] = name.lower()
        return type.__new__(cls, name, parents, args, **kwargs)


@add_metaclass(TablenameMeta)
class BaseModel(jsonmodels.models.Base):
    pass
