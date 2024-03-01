from sciroccoclient.exceptions import SciroccoHTTPDAOError
from sciroccoclient.http.base import Base
from sciroccoclient.responses import ClientMessageResponse
from sciroccoclient.systemdata import SystemData


class MessageDAO(Base):
    def __init__(self, request_adapter, system_data_hydrator):
        super().__init__()
        self.request_adapter = request_adapter
        self.system_data_hydrator = system_data_hydrator
        self.end_point = '/messages'

    def get_one(self, id):
        request_response = self.request_adapter.request('GET', ''.join([self.end_point, '/', id]))

        if request_response.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data

            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)

    def get_all(self):
        request_response = self.request_adapter.request('GET', self.end_point)

        if request_response.http_status is 200:
            responses = []

            for m in request_response.message_data:

                sr = ClientMessageResponse()
                sr.system_data = self.system_data_hydrator.hydrate_from_fields(SystemData(), m)
                sr.message_data = m['data']
                responses.append(sr)

            return responses
        elif request_response.http_status is 204:
            return None
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)

    def delete_one(self, id):
        request_response = self.request_adapter.request('DELETE', ''.join([self.end_point, '/', id]))
        if request_response.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data
            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)

    def delete_all(self):
        request_result = self.request_adapter.request('DELETE', self.end_point)
        if request_result.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_result.system_data
            ro.message_data = request_result.message_data
            return ro
        else:
            raise SciroccoHTTPDAOError(request_result.http_status)

    def update_one(self, id, message):
        request_response = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', id]), message)
        if request_response.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data
            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)
