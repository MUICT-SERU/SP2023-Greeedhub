import urllib3

from sciroccoclient.client import Client
from sciroccoclient.http.messagedao import MessageDAO
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.http.requestadapter import RequestsAdapter, RequestManagerResponseHandler, \
    RequestAdapterDataResponseHandler, RequestAdapterContentTypeDetector
from sciroccoclient.metadata import MetaDataDescriptor, MetaData, MetaDataHTTPHeadersFilter, \
    MetaDataHydrator


class ClientFactory:
    def get_http_client(self, api_url, node_id, auth_token):
        metadata_entity = MetaData()
        metadata_hydrator = MetaDataHydrator()
        metadata_descriptor = MetaDataDescriptor(metadata_entity)
        system_headers_filter = MetaDataHTTPHeadersFilter(metadata_descriptor)

        request_manager_response_handler = RequestManagerResponseHandler(system_headers_filter,
                                                                         metadata_hydrator,
                                                                         RequestAdapterDataResponseHandler())

        request_adapter = RequestsAdapter(
            urllib3.PoolManager(),
            request_manager_response_handler, metadata_descriptor, RequestAdapterContentTypeDetector())
        request_adapter.api_url = api_url
        request_adapter.node_id = node_id
        request_adapter.auth_token = auth_token

        message_dao = MessageDAO(request_adapter, metadata_hydrator)
        message_queue_dao = MessageQueueDAO(request_adapter, metadata_descriptor)

        client = Client(message_dao, message_queue_dao)

        return client

    def get_mongo_client(self):
        # TODO IMPLEMENT THIS FOR A DIRECT DB CLIENT. ONLY FOR INTERNAL PROCESS ACTIONS.
        raise NotImplementedError
