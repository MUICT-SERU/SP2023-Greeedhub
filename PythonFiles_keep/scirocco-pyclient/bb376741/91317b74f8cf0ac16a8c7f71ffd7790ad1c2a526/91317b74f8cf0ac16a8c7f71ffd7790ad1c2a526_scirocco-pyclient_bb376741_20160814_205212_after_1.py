import urllib3

from pyddsclient.client import Client
from pyddsclient.httpdao.batchdao import BatchDAO
from pyddsclient.httpdao.batchqueuedao import BatchQueueDAO
from pyddsclient.httpdao.messagedao import MessageDAO
from pyddsclient.httpdao.messagequeuedao import MessageQueueDAO
from pyddsclient.httpdao.requestsadapter import RequestsAdapter, RequestManagerResponseHandler


class ClientFactory(object):
    def get_http_client(self, node_id, auth_token):
        request_adapter = RequestsAdapter(node_id, auth_token, urllib3.PoolManager(), RequestManagerResponseHandler())
        message_dao = MessageDAO(request_adapter)
        message_queue_dao = MessageQueueDAO(request_adapter)
        batch_dao = BatchDAO(request_adapter)
        batch_queue_dao = BatchQueueDAO(request_adapter)

        client = Client(message_dao, message_queue_dao, batch_dao, batch_queue_dao)

        return client

    def get_mongo_client(self):
        # TODO IMPLEMENT THIS FOR A DIRECT DB CLIENT. ONLY FOR INTERNAL PROECESS ACTIONS.
        raise NotImplementedError
