class MessageQueueDAO(object):
    def __init__(self, request_adapter):
        self.request_adapter = request_adapter
        self.end_point = '/messageQueue'

    def pull(self, quantity=1):

        fields = {
            "quantity": quantity
        }
        return self.request_adapter.request('GET', self.end_point, fields)

    def push(self, msg):

        return self.request_adapter.request('POST', self.end_point, msg)


