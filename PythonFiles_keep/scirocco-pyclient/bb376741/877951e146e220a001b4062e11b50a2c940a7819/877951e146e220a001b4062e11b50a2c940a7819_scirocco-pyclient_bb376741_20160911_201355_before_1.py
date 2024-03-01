from urllib3._collections import HTTPHeaderDict


class SystemDataHTTPSplitter:
    http_system_headers_prefix = 'Scirocco'

    def __init__(self, system_data_entity, http_headers):
        self.system_data = system_data_entity
        self.http_headers = http_headers

    def get_system_headers(self):

        headers = []
        for sh in self.system_data.__dict__:
            header = '-'.join([self.http_system_headers_prefix, sh[1:].replace("_", "-").title()])
            headers.append(header)

        return headers

    def extract_system_data(self):

        system_data = SystemData()
        system_headers = self.get_system_headers()
        for k, v in self.http_headers.items():
            if k in system_headers:
                attr_name = k.replace(self.http_system_headers_prefix + '-', '')
                attr_name = attr_name.lower().replace('-', '_')
                if attr_name == 'from':
                    attr_name = attr_name + 'm'
                setattr(system_data, attr_name, v)

        return system_data

    def extract_http_headers(self):

        system_headers = self.get_system_headers()
        http_headers = HTTPHeaderDict()

        for k, v in self.http_headers.items():
            if k not in system_headers:
                http_headers.add(k, v)
        return http_headers


class SystemData:
    def __init__(self):
        self._from = None
        self._to = None
        self._id = None
        self._topic = None
        self._status = None
        self._update_time = None
        self._created_time = None
        self._scheduled_time = None
        self._error_time = None
        self._processed_time = None
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
    def tries(self):
        return self._tries

    @tries.setter
    def tries(self, data):
        self._tries = data
