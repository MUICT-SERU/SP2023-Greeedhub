from sciroccoclient.exceptions import SciroccoHTTPDAOError, SciroccoInvalidMessageError, \
    SciroccoInvalidMessageDataError, SciroccoInvalidMessageDestinationError, SciroccoInvalidMessageStatusError
from sciroccoclient.http.base import Base
from sciroccoclient.messages import SciroccoMessage
from sciroccoclient.responses import ClientMessageResponse


class MessageQueueDAO(Base):
    def __init__(self, request_adapter, metadata_descriptor):
        super().__init__()
        self.request_adapter = request_adapter
        self.metadata_descriptor = metadata_descriptor
        self.end_point = '/messageQueue'

    def pull(self):

        request_response = self.request_adapter.request('GET', self.end_point)

        if request_response.http_status is 200:
            ro = ClientMessageResponse()
            ro.metadata = request_response.metadata
            ro.payload = request_response.payload

            return ro
        elif request_response.http_status is 204:
            return None
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)

    def push(self, message):
        # Todo , next refactor, move this to its own validator class.
        if not isinstance(message, SciroccoMessage):
            raise SciroccoInvalidMessageError
        if not message.node_destination:
            raise SciroccoInvalidMessageDestinationError
        if not message.status:
            raise SciroccoInvalidMessageStatusError
        if not message.payload:
            raise SciroccoInvalidMessageDataError

        headers = {
            self.metadata_descriptor.get_http_header_by_field_name('node_destination'): message.node_destination,
            self.metadata_descriptor.get_http_header_by_field_name('status'): message.status
        }

        if message.payload_type:
            headers.update({self.metadata_descriptor.get_http_header_by_field_name('payload_type'): message.payload_type
                            })
        if message.status == 'scheduled' and message.scheduled_time:
            headers.update(
                {self.metadata_descriptor.get_http_header_by_field_name('scheduled_time'): message.scheduled_time})

        request_response = self.request_adapter.request('POST', self.end_point, message.payload, headers)

        if request_response.http_status is 201:
            ro = ClientMessageResponse()
            ro.metadata = request_response.metadata
            ro.payload = request_response.payload
            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)

    def ack(self, msg_id):
        request_response = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', msg_id, '/ack']))

        if request_response.http_status == 200:
            ro = ClientMessageResponse()
            ro.metadata = request_response.metadata
            ro.payload = request_response.payload
            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)
