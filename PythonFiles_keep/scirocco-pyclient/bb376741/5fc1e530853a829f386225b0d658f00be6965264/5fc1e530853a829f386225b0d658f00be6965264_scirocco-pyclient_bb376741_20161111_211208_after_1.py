import urllib3

from sciroccoclient.client import Client
from sciroccoclient.http.messagedao import MessageDAO
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.http.requestadapter import RequestsAdapter, RequestManagerResponseHandler, \
    RequestAdapterDataResponseHandler, RequestAdapterContentTypeDetector
from sciroccoclient.systemdata import SystemDataDescriptor, SystemData, SystemDataHTTPHeadersFilter, \
    SystemDataHydrator


class ClientFactory:
    def get_http_client(self, api_url, node_id, auth_token):
        system_data_entity = SystemData()
        system_data_hydrator = SystemDataHydrator()
        system_data_descriptor = SystemDataDescriptor(system_data_entity)
        system_headers_filter = SystemDataHTTPHeadersFilter(system_data_descriptor)

        request_manager_response_handler = RequestManagerResponseHandler(system_headers_filter,
                                                                         system_data_hydrator,
                                                                         RequestAdapterDataResponseHandler())

        request_adapter = RequestsAdapter(
            urllib3.PoolManager(),
            request_manager_response_handler, system_data_descriptor, RequestAdapterContentTypeDetector())
        request_adapter.api_url = api_url
        request_adapter.node_id = node_id
        request_adapter.auth_token = auth_token

        message_dao = MessageDAO(request_adapter, system_data_hydrator)
        message_queue_dao = MessageQueueDAO(request_adapter, system_data_descriptor)

        client = Client(message_dao, message_queue_dao)

        return client

    def get_mongo_client(self):
        # TODO IMPLEMENT THIS FOR A DIRECT DB CLIENT. ONLY FOR INTERNAL PROCESS ACTIONS.
        raise NotImplementedError
