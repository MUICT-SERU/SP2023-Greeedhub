import datetime

from sciroccoclient.exceptions import SciroccoInvalidMessageScheduleTimeError, SciroccoInvalidMessageStatusError


class SciroccoMessage:
    def __init__(self):
        self._destination = None
        self._status = 'pending'
        self._data = None
        self._data_type = None
        self._scheduled_time = None

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, destination):
        self._destination = destination

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status not in ['pending', 'scheduled']:
            raise SciroccoInvalidMessageStatusError
        self._status = status

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        self._data_type = data_type

    @property
    def scheduled_time(self):
        return self._scheduled_time

    @scheduled_time.setter
    def scheduled_time(self, scheduled_time):
        if not isinstance(scheduled_time, datetime.datetime):
            raise SciroccoInvalidMessageScheduleTimeError
        self._scheduled_time = scheduled_time.isoformat()
        self.status = 'scheduled'



