class Client:
    def __init__(self, message_dao, message_queue_dao):
        self.message_dao = message_dao
        self.message_queue_dao = message_queue_dao

    def message_get(self, id):
        return self.message_dao.get_one(id)

    def message_get_all(self):
        return self.message_dao.get_all()

    def message_delete_one(self, id):
        return self.message_dao.delete_one(id)

    def message_delete_all(self):
        return self.message_dao.delete_all()

    def message_update_one(self, id, message):
        return self.message_dao.update_one(id, message)

    def message_queue_pull(self):
        return self.message_queue_dao.pull()

    def message_queue_push(self, id, msg):
        return self.message_queue_dao.push(id, msg)

    def message_queue_ack(self, msg_id):
        return self.message_queue_dao.ack(msg_id)
