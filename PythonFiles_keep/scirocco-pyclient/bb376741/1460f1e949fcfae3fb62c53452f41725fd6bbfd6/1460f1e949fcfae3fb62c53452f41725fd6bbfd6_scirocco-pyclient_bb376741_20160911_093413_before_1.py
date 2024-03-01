import json

from urllib3.request import urlencode


class RequestsAdapter:
    from_header = "Scirocco-From"

    def __init__(self, api_url, node_id, auth_token, request_manager, request_manager_response_handler):
        self._api_url = api_url
        self._node_id = node_id
        self._auth_token = auth_token
        self.request_manager = request_manager
        self.request_manager_response_handler = request_manager_response_handler

    @property
    def api_url(self):
        return self._api_url

    @property
    def node_id(self):
        return self._node_id

    @property
    def auth_token(self):
        return self._auth_token

    def get_fixed_headers(self):

        return {
            self.from_header: self._node_id,
            'Authorization': self._auth_token
        }

    def get_uri(self, resource):

        url = '/'.join([self.api_url, resource.strip("/")])
        return url

    def request(self, method, resource='', data=None, headers=None):

        method = method.upper()
        url = self.get_uri(resource)

        if isinstance(headers, dict):
            headers.update(self.get_fixed_headers())
        else:
            headers = self.get_fixed_headers()

        if isinstance(data, dict):

            if method in ['GET', 'DELETE']:
                url = ''.join([url, '?', urlencode(data)])
                data = None
            else:
                data = json.dumps(data)
        request_manager_result = self.request_manager.urlopen(method, url, headers=headers, body=data)

        return self.request_manager_response_handler.handle(request_manager_result)


class RequestManagerResponseHandler:
    def handle(self, response):
        ro = RequestAdapterResponse()

        ro.http_headers = self.treat_headers(response.headers)
        ro.http_status = response.status
        ro.system_data = self.extract_system_data(response.headers)
        ro.message_data = self.treat_data(response.data)
        return ro

    def extract_system_data(self, headers):

        return {k: v for k, v in headers.items() if k in self.get_system_headers()}

    def treat_data(self, data):

        try:
            return json.loads(data.decode())
        except ValueError or TypeError:
            return data.decode()

    def treat_headers(self, headers):

        return headers

    @staticmethod
    def get_system_headers():
        return [

            "Scirocco-From",
            "Scirocco-To",
            "Scirocco-Id",
            "Scirocco-Topic",
            "Scirocco-Status",
            "Scirocco-Update-Time",
            "Scirocco-Created-Time",
            "Scirocco-Scheduled-Time",
            "Scirocco-Error-Time",
            "Scirocco-Processed-Time",
            "Scirocco-Tries"
        ]


class RequestAdapterResponse:
    def __init__(self):
        self._system_data = None
        self._message_data = None
        self._http_headers = None
        self._http_status = None

    @property
    def system_data(self):
        return self._system_data

    @system_data.setter
    def system_data(self, data):
        self._system_data = data

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, data):
        self._message_data = data

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
