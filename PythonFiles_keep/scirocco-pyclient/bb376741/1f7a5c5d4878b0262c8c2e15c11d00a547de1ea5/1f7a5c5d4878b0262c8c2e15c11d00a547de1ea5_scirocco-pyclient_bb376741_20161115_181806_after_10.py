from urllib3._collections import HTTPHeaderDict


class MetaDataHydrator:

    def hydrate_from_headers(self, metadata_entity, http_input_headers):

        for k, v in http_input_headers.items():
            attr_name = k.replace(MetaDataDescriptor.prefix + '-', '')
            attr_name = attr_name.lower().replace('-', '_')
            if hasattr(metadata_entity, attr_name):
                setattr(metadata_entity, attr_name, v)

        return metadata_entity

    def hydrate_from_fields(self, metadata_entity, fields):

        for k, v in fields.items():
            if hasattr(metadata_entity, k):
                setattr(metadata_entity, k, v)
        return metadata_entity




class MetaDataHTTPHeadersFilter:
    def __init__(self, metadata_descriptor):
        self.metadata_descriptor = metadata_descriptor
        self.system_headers = metadata_descriptor.get_all_http_headers()

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


class MetaDataDescriptor:
    prefix = 'Scirocco'
    separator = '-'

    def __init__(self, metadata_entity):

        if not isinstance(metadata_entity, MetaData):
            raise TypeError

        self.metadata_entity = metadata_entity

    def _compose_http_header_from_field_name(self, name):

        parts = list(filter(None, name.split('_')))
        filtered_parts = []
        for p in parts:
            p = p.replace('_', '').title()
            filtered_parts.append(p)
        filtered_parts.insert(0, self.prefix)
        header = self.separator.join(filtered_parts)
        return header

    def get_all_fields(self):
        fields = []
        for sh in self.metadata_entity.__dict__:
            if not sh.startswith("__"):
                fields.append(sh)
        return fields

    def get_all_http_headers(self):

        headers = []
        for sh in self.get_all_fields():
            headers.append(self._compose_http_header_from_field_name(sh))

        return headers

    def get_http_header_by_field_name(self, name):

        if hasattr(self.metadata_entity, name):
            return self._compose_http_header_from_field_name(name)
        else:
            raise AttributeError


class MetaData:
    def __init__(self):
        self._node_destination = None
        self._node_source = None
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
        self._payload_type = None

    @property
    def node_source(self):
        return self._node_source

    @node_source.setter
    def node_source(self, node_source):
        self._node_source = node_source

    @property
    def node_destination(self):
        return self._node_destination

    @node_destination.setter
    def node_destination(self, node_destination):
        self._node_destination = node_destination

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
    def payload_type(self):
        return self._payload_type

    @payload_type.setter
    def payload_type(self, payload_type):
        self._payload_type = payload_type
