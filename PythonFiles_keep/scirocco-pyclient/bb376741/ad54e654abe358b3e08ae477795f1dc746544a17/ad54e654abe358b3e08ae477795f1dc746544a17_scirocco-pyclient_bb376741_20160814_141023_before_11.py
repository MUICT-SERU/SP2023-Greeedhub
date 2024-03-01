class BatchQueueDAO(object):
    def __init__(self, request_adapter):
        self.request_adapter = request_adapter
        self.end_point = '/batchQueue'

    def pull(self):
        return self.request_adapter.request('GET', self.end_point)

    def push(self, batch):
        return self.request_adapter.request('POST', self.end_point, batch)

    def ack(self, batch_id):
        return self.request_adapter.request('PATCH', self.end_point + '/' + batch_id + '/ack')
