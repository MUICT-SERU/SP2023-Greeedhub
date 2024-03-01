from urllib3._collections import HTTPHeaderDict


class SystemDataHydrator:

    def hydrate_from_headers(self, system_data_entity, http_input_headers):

        for k, v in http_input_headers.items():
            attr_name = k.replace(SystemDataDescriptor.prefix + '-', '')
            attr_name = attr_name.lower().replace('-', '_')
            attr_name = self.perform_nomenclature_adjustments(attr_name)
            if hasattr(system_data_entity, attr_name):
                setattr(system_data_entity, attr_name, v)

        return system_data_entity

    def hydrate_from_fields(self, system_data_entity, fields):

        for k, v in fields.items():
            attr_name = self.perform_nomenclature_adjustments(k)
            if hasattr(system_data_entity, attr_name):
                setattr(system_data_entity, attr_name, v)
        return system_data_entity

    def perform_nomenclature_adjustments(self, name):
        if name == 'from':
            name += 'm'
        return name


class SystemDataHTTPHeadersFilter:
    def __init__(self, system_data_descriptor):
        self.system_data_descriptor = system_data_descriptor
        self.system_headers = system_data_descriptor.get_all_http_headers()

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


class SystemDataDescriptor:
    prefix = 'Scirocco'
    separator = '-'

    def __init__(self, system_data_entity):

        if not isinstance(system_data_entity, SystemData):
            raise TypeError

        self.system_data_entity = system_data_entity

    def _compose_http_header_from_field_name(self, name):

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

    def get_all_fields(self):
        fields = []
        for sh in self.system_data_entity.__dict__:
            if not sh.startswith("__"):
                fields.append(sh)
        return fields

    def get_all_http_headers(self):

        headers = []
        for sh in self.get_all_fields():
            headers.append(self._compose_http_header_from_field_name(sh))

        return headers

    def get_http_header_by_field_name(self, name):

        if hasattr(self.system_data_entity, name):
            return self._compose_http_header_from_field_name(name)
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
