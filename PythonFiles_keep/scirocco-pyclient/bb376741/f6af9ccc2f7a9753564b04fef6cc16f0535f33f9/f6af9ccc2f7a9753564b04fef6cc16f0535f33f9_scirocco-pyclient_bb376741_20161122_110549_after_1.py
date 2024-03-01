from sciroccoclient.messages import SciroccoMessage

from sciroccoclient.clients import HTTPClient


class ClientExample:
    def __init__(self):
        pass

    def run(self):

        c = HTTPClient('http://localhost', 'af123', 'DEFAULT_TOKEN')
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = '{"as":"sd"}'
        res = c.push(message)
        print(res.payload)
        res = c.pull()
        print(res.payload)
        res = c.ack(res.metadata.id)


if __name__ == '__main__':
    p = ClientExample()
    p.run()
