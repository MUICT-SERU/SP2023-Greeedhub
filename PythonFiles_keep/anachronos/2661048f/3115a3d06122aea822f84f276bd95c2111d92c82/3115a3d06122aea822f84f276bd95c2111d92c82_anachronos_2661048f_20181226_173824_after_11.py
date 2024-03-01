from datetime import datetime


class Message(object):

    def __init__(self, time: datetime, payload):
        self.time = time
        self.payload = payload
