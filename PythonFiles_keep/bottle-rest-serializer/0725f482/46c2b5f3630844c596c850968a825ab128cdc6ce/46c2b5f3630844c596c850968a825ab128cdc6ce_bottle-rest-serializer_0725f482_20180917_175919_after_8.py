from datetime import datetime
from decimal import Decimal
from json import dumps, JSONEncoder

from bottle import JSONPlugin


class __FlexibleJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj.isoformat())
        elif isinstance(self, Decimal):
            return float(obj)
        return JSONEncoder.default(self, obj)


class FlexibleJSONPlugin(JSONPlugin):

    def __init__(self):
        super().__init__(lambda obj: dumps(obj, cls=__FlexibleJSONEncoder))
