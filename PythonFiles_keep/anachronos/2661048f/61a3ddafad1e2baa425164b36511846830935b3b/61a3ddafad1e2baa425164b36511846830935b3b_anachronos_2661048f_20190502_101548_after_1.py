import requests

from anachronos.compat.jivago_streams import Stream


class HttpRequester(object):

    def __init__(self, host='localhost', port=4000, path='', default_arguments: dict = None):
        self.path = path
        self.host = host
        self.port = port

        if default_arguments is None:
            default_arguments = {}

        self.default_arguments = default_arguments

    def with_path(self, sub_path: str) -> "HttpRequester":
        return HttpRequester(self.host, self.port, sub_path, default_arguments=self.default_arguments)

    def append_path(self, sub_path: str) -> "HttpRequester":
        return HttpRequester(self.host, self.port, self.path + sub_path, default_arguments=self.default_arguments)

    def get(self, path: str, *args, **kwargs):
        return requests.get(self.get_full_url(path), *args, **self._join_arg_dict(self.default_arguments, kwargs))

    def post(self, path: str, *args, **kwargs):
        return requests.post(self.get_full_url(path), *args, **self._join_arg_dict(self.default_arguments, kwargs))

    def put(self, path: str, *args, **kwargs):
        return requests.put(self.get_full_url(path), *args, **self._join_arg_dict(self.default_arguments, kwargs))

    def patch(self, path, *args, **kwargs):
        return requests.patch(self.get_full_url(path), *args, **self._join_arg_dict(self.default_arguments, kwargs))

    def head(self, path, **kwargs):
        return requests.head(self.get_full_url(path), **self._join_arg_dict(self.default_arguments, kwargs))

    def options(self, path, **kwargs):
        return requests.options(self.get_full_url(path), **self._join_arg_dict(self.default_arguments, kwargs))

    def get_full_url(self, path):
        return f"{self.host}:{self.port}{self.path}{path}"

    def _join_arg_dict(self, dict1, dict2) -> dict:
        return {**dict1, **dict2}
