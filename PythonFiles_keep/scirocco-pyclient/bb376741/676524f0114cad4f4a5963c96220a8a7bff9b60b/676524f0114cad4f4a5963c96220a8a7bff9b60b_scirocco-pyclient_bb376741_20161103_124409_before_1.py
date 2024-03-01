import urllib3

from sciroccoclient.client import Client
from sciroccoclient.http.messagedao import MessageDAO
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.http.requestadapter import RequestsAdapter, RequestManagerResponseHandler


class ClientFactory:
    def get_http_client(self, api_url, node_id, auth_token):
        request_adapter = RequestsAdapter(api_url, node_id, auth_token, urllib3.PoolManager(),
                                          RequestManagerResponseHandler())
        message_dao = MessageDAO(request_adapter)
        message_queue_dao = MessageQueueDAO(request_adapter)

        client = Client(message_dao, message_queue_dao)

        return client

    def get_mongo_client(self):
        # TODO IMPLEMENT THIS FOR A DIRECT DB CLIENT. ONLY FOR INTERNAL PROCESS ACTIONS.
        raise NotImplementedError
