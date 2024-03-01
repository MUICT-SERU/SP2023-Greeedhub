from sciroccoclient.clients import HTTPClient


class ClientExample:

    @staticmethod
    def on_message_cb(dao, msg):
        print(msg.payload)
        dao.ack(msg.metadata.id)

    def run(self):
        print("Im ready, send me a message.")
        c = HTTPClient('http://localhost', 'af123', 'DEFAULT_TOKEN')
        c.on_receive(ClientExample.on_message_cb)


if __name__ == '__main__':
    p = ClientExample()
    p.run()
