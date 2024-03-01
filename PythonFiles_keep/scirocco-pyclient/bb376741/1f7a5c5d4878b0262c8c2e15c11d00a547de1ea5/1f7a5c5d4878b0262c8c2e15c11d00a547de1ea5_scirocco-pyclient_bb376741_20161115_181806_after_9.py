import datetime

from sciroccoclient.exceptions import SciroccoInvalidMessageScheduleTimeError, SciroccoInvalidMessageStatusError


class SciroccoMessage:
    def __init__(self):
        self._node_destination = None
        self._status = 'pending'
        self._payload = None
        self._payload_type = None
        self._scheduled_time = None

    @property
    def node_destination(self):
        return self._node_destination

    @node_destination.setter
    def node_destination(self, node_destination):
        self._node_destination = node_destination

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status not in ['pending', 'scheduled']:
            raise SciroccoInvalidMessageStatusError
        self._status = status

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload

    @property
    def payload_type(self):
        return self._payload_type

    @payload_type.setter
    def payload_type(self, payload_type):
        self._payload_type = payload_type

    @property
    def scheduled_time(self):
        return self._scheduled_time

    @scheduled_time.setter
    def scheduled_time(self, scheduled_time):
        if not isinstance(scheduled_time, datetime.datetime):
            raise SciroccoInvalidMessageScheduleTimeError
        self._scheduled_time = scheduled_time.isoformat()
        self.status = 'scheduled'



