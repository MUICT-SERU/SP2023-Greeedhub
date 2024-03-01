class MessageDAO(object):
    def __init__(self, request_adapter):
        self.request_adapter = request_adapter
        self.end_point = '/messages'

    def get_one(self, id):
        return self.request_adapter.request('GET', self.end_point + '/' + id)

    def get_all(self):
        return self.request_adapter.request('GET', self.end_point)

    def delete_one(self, id):
        return self.request_adapter.request('DELETE', self.end_point + '/' + id)

    def delete_all(self):
        return self.request_adapter.request('DELETE', self.end_point)

    def update_one(self, id, message):
        return self.request_adapter.request('PATCH', self.end_point + '/' + id, message)
