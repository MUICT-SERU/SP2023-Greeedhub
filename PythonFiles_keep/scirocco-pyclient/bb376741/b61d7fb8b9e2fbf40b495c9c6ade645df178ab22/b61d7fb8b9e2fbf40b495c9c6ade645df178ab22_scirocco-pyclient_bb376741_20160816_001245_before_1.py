from pyddsclient.httpclient import HTTPClient


class ClientClass(object):
    def __init__(self):
        pass

    def run(self):
        c = HTTPClient('af123', 'dd52bb39d5a1bd8f6235dbef7df26d3e')
        res = c.message_queue_push({"to_node_id": "af123", "data": {"as":"sd"}})
        print(res.__dict__)
        res = c.message_queue_pull()
        print(res.__dict__)
        res = c.message_queue_pull()
        print(res.__dict__)


if __name__ == '__main__':
    p = ClientClass()
    p.run()
