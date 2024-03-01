class Client:
    def __init__(self, message_dao, message_queue_dao):
        self.message_dao = message_dao
        self.message_queue_dao = message_queue_dao

    def get(self, msg_id):
        return self.message_dao.get_one(msg_id)

    def get_all(self):
        return self.message_dao.get_all()

    def delete_one(self, msg_id):
        return self.message_dao.delete_one(msg_id)

    def delete_all(self):
        return self.message_dao.delete_all()

    def update_one(self, msg_id, new_payload):
        return self.message_dao.update_one(msg_id, new_payload)

    def pull(self):
        return self.message_queue_dao.pull()

    def push(self, message):
        return self.message_queue_dao.push(message)

    def ack(self, msg_id):
        return self.message_queue_dao.ack(msg_id)
