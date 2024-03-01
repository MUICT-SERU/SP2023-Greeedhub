from pyddsclient.httpdao.base import Base


class BatchDAO(Base):
    def __init__(self, request_adapter):
        super().__init__()
        self.request_adapter = request_adapter
        self.end_point = '/batches'

    def get_all(self):
        return self.request_adapter.request('GET', self.end_point)

    def get_one(self, id):
        return self.request_adapter.request('GET', ''.join([self.end_point, '/', id]))

    def delete_one(self, id):
        return self.request_adapter.request('DELETE', ''.join([self.end_point, '/', id]))

    def delete_all(self):
        return self.request_adapter.request('DELETE', self.end_point)

    def update_one(self, id, data):
        return self.request_adapter.request('PATCH', ''.join([self.end_point, '/', id]), data)
