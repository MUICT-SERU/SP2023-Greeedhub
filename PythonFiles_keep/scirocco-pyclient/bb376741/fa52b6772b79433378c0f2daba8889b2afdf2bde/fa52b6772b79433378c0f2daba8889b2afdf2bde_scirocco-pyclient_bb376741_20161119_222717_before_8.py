import json

from urllib3.exceptions import HTTPError
from urllib3.request import urlencode

from sciroccoclient.exceptions import SciroccoRequestAdapterError, SciroccoInitParamsError
from sciroccoclient.metadata import MetaData


class RequestsAdapter:
    def __init__(self, request_manager, request_manager_response_handler,
                 meta_data_http, content_type_detector):
        self._api_url = None
        self._node_id = None
        self._auth_token = None
        self.request_manager = request_manager
        self.request_manager_response_handler = request_manager_response_handler
        self.meta_data_http = meta_data_http
        self.content_type_detector = content_type_detector

    @property
    def api_url(self):
        return self._api_url

    @api_url.setter
    def api_url(self, api_url):
        self._api_url = api_url

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, node_id):
        self._node_id = node_id

    @property
    def auth_token(self):
        return self._auth_token

    @auth_token.setter
    def auth_token(self, auth_token):
        self._auth_token = auth_token

    def get_fixed_headers(self):

        return {
            self.meta_data_http.get_http_header_by_field_name('node_source'): self._node_id,
            'Authorization': self._auth_token
        }

    def get_uri(self, resource):

        url = '/'.join([self.api_url, resource.strip("/")])
        return url

    def request(self, method, resource='', data=None, headers=None):

        if self.api_url is None or self.auth_token is None or self.node_id is None:
            raise SciroccoInitParamsError

        method = method.upper()
        url = self.get_uri(resource)

        if isinstance(headers, dict):
            headers.update(self.get_fixed_headers())
        else:
            headers = self.get_fixed_headers()

        headers.update({"Content-Type": self.content_type_detector.detect_from_body(data)})

        if isinstance(data, dict):

            if method in ['GET', 'DELETE']:
                url = ''.join([url, '?', urlencode(data)])
                data = None
            else:
                data = json.dumps(data)
        try:
            request_manager_result = self.request_manager.urlopen(method, url, headers=headers, body=data)
            return self.request_manager_response_handler.handle(request_manager_result)

        except HTTPError as e:
            SciroccoRequestAdapterError(e)


class RequestManagerResponseHandler:
    def __init__(self, metadata_http_headers_filter, metadata_hydrator, data_treatment):
        self.metadata_http_headers_filter = metadata_http_headers_filter
        self.metadata_hydrator = metadata_hydrator
        self.data_treatment = data_treatment

    def handle(self, response):
        ro = RequestAdapterResponse()
        system_headers = self.metadata_http_headers_filter.filter_system(response.headers)
        ro.metadata = self.metadata_hydrator.hydrate_from_headers(MetaData(), system_headers)
        ro.http_headers = self.metadata_http_headers_filter.filter_http(response.headers)
        ro.http_status = response.status
        ro.payload = self.data_treatment.treat(response.data)
        return ro


class RequestAdapterDataResponseHandler:
    def treat(self, data):

        try:
            return json.loads(data.decode())
        except ValueError or TypeError:
            try:
                return data.decode()
            except UnicodeDecodeError:
                return data


class RequestAdapterContentTypeDetector:
    def __init__(self):

        self.default_type = 'application/octet-stream'

    def detect_from_body(self, body):

        if self.check_for_binary(body):
            return self.default_type
        elif self.check_for_object(body):
            return 'application/json'
        elif self.check_for_string(body):
            return 'text/plain'
        else:
            return self.default_type

    def check_for_string(self, data):
        return type(data) is str

    def check_for_object(self, data):

        try:
            if type(data) is str:
                json.loads(data)
            elif type(data) is dict:
                json.dumps(data)
            else:
                return False
            return True
        except:
            return False

    def check_for_binary(self, data):
        return type(data) is bytes


class RequestAdapterResponse:
    def __init__(self):
        self._metadata = None
        self._payload = None
        self._http_headers = None
        self._http_status = None

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, data):
        self._metadata = data

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload

    @property
    def http_headers(self):
        return self._http_headers

    @http_headers.setter
    def http_headers(self, data):
        self._http_headers = data

    @property
    def http_status(self):
        return self._http_status

    @http_status.setter
    def http_status(self, status):
        self._http_status = status
