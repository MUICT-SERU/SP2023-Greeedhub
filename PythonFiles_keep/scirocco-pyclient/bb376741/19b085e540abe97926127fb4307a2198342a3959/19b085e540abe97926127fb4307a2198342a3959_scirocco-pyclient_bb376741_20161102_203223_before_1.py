from urllib3._collections import HTTPHeaderDict


class SystemDataHTTPSplitter:
    def __init__(self, system_data_entity, http_headers):
        self.system_data = system_data_entity
        self.http_headers = http_headers
        self.system_headers = SystemDataHTTPHeaders.get_system_headers()

    def extract_system_data(self):

        system_data = SystemData()
        for k, v in self.http_headers.items():
            if k in self.system_headers:
                attr_name = k.replace(SystemDataHTTPHeaders.prefix + '-', '')
                attr_name = attr_name.lower().replace('-', '_')
                if attr_name == 'from':
                    attr_name += 'm'
                setattr(system_data, attr_name, v)

        return system_data

    def extract_http_headers(self):

        http_headers = HTTPHeaderDict()

        for k, v in self.http_headers.items():
            if k not in self.system_headers:
                http_headers.add(k, v)
        return http_headers


"""
This two objects may need to be simetric. If you want to update or add some system headers
do it in both of them. First object is for simply decouple headers name. Second its an entity and carries
system data between objects at runtime.
"""


class SystemDataHTTPHeaders:
    prefix = 'Scirocco'
    to = '-'.join([prefix, 'To'])
    fromm = '-'.join([prefix, 'From'])
    id = '-'.join([prefix, 'Id'])
    topic = '-'.join([prefix, 'Topic'])
    status = '-'.join([prefix, 'Status'])
    update_time = '-'.join([prefix, 'Update', 'Time'])
    created_time = '-'.join([prefix, 'Created', 'Time'])
    scheduled_time = '-'.join([prefix, 'Scheduled', 'Time'])
    error_time = '-'.join([prefix, 'Error', 'Time'])
    processed_time = '-'.join([prefix, 'Processed', 'Time'])
    processing_time = '-'.join([prefix, 'Processing', 'Time'])
    tries = '-'.join([prefix, 'Tries'])

    @staticmethod
    def get_system_headers():

        headers = []
        for sh in SystemDataHTTPHeaders.__dict__:
            if sh not in ['prefix', 'get_system_headers'] and not sh.startswith("__"):
                if sh == 'fromm':
                    sh = sh[:-1]
                header = '-'.join([SystemDataHTTPHeaders.prefix, sh.replace("_", "-").title()])
                headers.append(header)

        return headers


class SystemData:
    def __init__(self):
        self._to = None
        self._from = None
        self._id = None
        self._topic = None
        self._status = None
        self._update_time = None
        self._created_time = None
        self._scheduled_time = None
        self._error_time = None
        self._processed_time = None
        self._processing_time = None
        self._tries = None

    @property
    def fromm(self):
        return self._from

    @fromm.setter
    def fromm(self, data):
        self._from = data

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, data):
        self._to = data

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, data):
        self._id = data

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, data):
        self._topic = data

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, data):
        self._status = data

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, data):
        self._update_time = data

    @property
    def created_time(self):
        return self._created_time

    @created_time.setter
    def created_time(self, data):
        self._created_time = data

    @property
    def scheduled_time(self):
        return self._scheduled_time

    @scheduled_time.setter
    def scheduled_time(self, data):
        self._scheduled_time = data

    @property
    def error_time(self):
        return self._error_time

    @error_time.setter
    def error_time(self, data):
        self._error_time = data

    @property
    def processed_time(self):
        return self._processed_time

    @processed_time.setter
    def processed_time(self, data):
        self._processed_time = data

    @property
    def processing_time(self):
        return self._processing_time

    @processing_time.setter
    def processing_time(self, data):
        self._processing_time = data

    @property
    def tries(self):
        return self._tries

    @tries.setter
    def tries(self, data):
        self._tries = data
