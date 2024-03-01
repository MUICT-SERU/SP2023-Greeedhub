from urllib3._collections import HTTPHeaderDict


class HTTP2SystemDataHydrator:
    def __init__(self, system_headers_filter):

        self.system_headers_filter = system_headers_filter

    def hydrate(self, system_data_entity, http_input_headers):

        filtered_headers = self.system_headers_filter.filter_system(http_input_headers)

        for k, v in filtered_headers.items():
            attr_name = k.replace(SystemDataHTTPHeadersDescriptor.prefix + '-', '')
            attr_name = attr_name.lower().replace('-', '_')
            if attr_name == 'from':
                attr_name += 'm'
            setattr(system_data_entity, attr_name, v)

        return system_data_entity


class SystemDataHTTPHeadersFilter:
    def __init__(self, system_data_http_descriptor):
        self.system_data_http_descriptor = system_data_http_descriptor
        self.system_headers = system_data_http_descriptor.get_all()

    def filter_system(self, http_input_headers):

        http_headers = HTTPHeaderDict()

        for k, v in http_input_headers.items():
            if k in self.system_headers:
                http_headers.add(k, v)
        return http_headers

    def filter_http(self, http_input_headers):

        http_headers = HTTPHeaderDict()

        for k, v in http_input_headers.items():
            if k not in self.system_headers:
                http_headers.add(k, v)
        return http_headers


class SystemDataHTTPHeadersDescriptor:
    prefix = 'Scirocco'
    separator = '-'

    def __init__(self, system_data_entity):

        if not isinstance(system_data_entity, SystemData):
            raise TypeError

        self.system_data_entity = system_data_entity

    def _compose_header(self, name):

        parts = list(filter(None, name.split('_')))
        filtered_parts = []
        for p in parts:
            if p == 'fromm':
                p = p[:-1]
            p = p.replace('_', '').title()
            filtered_parts.append(p)
        filtered_parts.insert(0, self.prefix)
        header = self.separator.join(filtered_parts)
        return header

    def get_all(self):

        headers = []
        for sh in self.system_data_entity.__dict__:
            if not sh.startswith("__"):
                headers.append(self._compose_header(sh))

        return headers

    def get_by_name(self, name):

        if hasattr(self.system_data_entity, name):
            return self._compose_header(name)
        else:
            raise AttributeError


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
        self._data_type = None

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

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data):
        self._data_type = data
