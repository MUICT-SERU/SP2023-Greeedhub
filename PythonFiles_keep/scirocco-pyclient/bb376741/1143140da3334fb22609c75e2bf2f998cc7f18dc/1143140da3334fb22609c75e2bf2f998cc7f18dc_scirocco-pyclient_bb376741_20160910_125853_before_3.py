from unittest.mock import MagicMock


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class RequestManagerMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def urlopen(self, method, url=None, headers=None, body=None):
        if headers is None:
            headers = {}
        headers['url'] = url
        headers['method'] = method

        return Bunch(data=body, headers=headers, status=200)
