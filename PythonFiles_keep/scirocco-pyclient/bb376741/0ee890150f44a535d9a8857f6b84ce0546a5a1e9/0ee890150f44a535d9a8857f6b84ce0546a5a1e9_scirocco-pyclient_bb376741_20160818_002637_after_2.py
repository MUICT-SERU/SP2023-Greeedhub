class Client:
    def __init__(self, message_dao, message_queue_dao, batch_dao, batch_queue_dao):
        self.message_dao = message_dao
        self.message_queue_dao = message_queue_dao
        self.batch_dao = batch_dao
        self.batch_queue_dao = batch_queue_dao

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

    def message_queue_pull(self, quantity=1):
        return self.message_queue_dao.pull(quantity)

    def message_queue_push(self, msg):
        return self.message_queue_dao.push(msg)

    def message_queue_ack(self, msg_id):
        return self.message_queue_dao.ack(msg_id)

    def message_queue_ack_group(self, msg_group_id):
        return self.message_queue_dao.ack_group(msg_group_id)

    def batch_get(self, id):
        return self.batch_dao.get_one(id)

    def batch_get_all(self):
        return self.batch_dao.get_all()

    def batch_delete_one(self, id):
        return self.batch_dao.delete_one(id)

    def batch_delete_all(self):
        return self.batch_dao.delete_all()

    def batch_update_one(self, id, batch):
        return self.batch_dao.update_one(id, batch)

    def batch_queue_pull(self):
        return self.batch_queue_dao.pull()

    def batch_queue_push(self, batch):
        return self.batch_queue_dao.push(batch)

    def batch_queue_ack(self, batch_id):
        return self.batch_queue_dao.ack(batch_id)
