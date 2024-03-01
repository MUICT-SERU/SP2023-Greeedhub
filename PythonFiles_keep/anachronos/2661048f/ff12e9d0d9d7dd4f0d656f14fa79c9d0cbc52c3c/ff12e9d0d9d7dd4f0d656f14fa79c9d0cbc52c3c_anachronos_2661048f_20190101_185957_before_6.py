import requests


class Requester(object):

    def __init__(self, host='localhost', port=4000, path=''):
        self.path = path
        self.host = host
        self.port = port

    def with_path(self, sub_path: str) -> "Requester":
        return Requester(self.host + sub_path, self.port)

    def get(self, path: str, *args, **kwargs):
        return requests.get(self.get_full_url(path), *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return requests.post(self.get_full_url(path), *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return requests.put(self.get_full_url(path), *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return requests.patch(self.get_full_url(path), *args, **kwargs)

    def head(self, path, **kwargs):
        return requests.head(self.get_full_url(path), **kwargs)

    def options(self, path, **kwargs):
        return requests.options(self.get_full_url(path), **kwargs)

    def get_full_url(self, path):
        return f"{self.host}:{self.port}{self.path}{path}"
