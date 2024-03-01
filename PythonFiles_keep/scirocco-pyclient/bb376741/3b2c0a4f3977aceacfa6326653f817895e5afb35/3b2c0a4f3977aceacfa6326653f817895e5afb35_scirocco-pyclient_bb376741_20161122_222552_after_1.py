import inspect
import time
import signal
from threading import Thread, Event

from sciroccoclient.exceptions import SciroccoInvalidOnReceiveCallBackError, SciroccoInterruptOnReceiveCallbackError


class Client:
    """
    The main facade with actors will interact to. It may be valid for al type of clients.
    """

    def __init__(self, message_dao, message_queue_dao, message_validator):
        self.message_dao = message_dao
        self.message_queue_dao = message_queue_dao
        self.message_validator = message_validator

    def get(self, msg_id):
        """

        :param msg_id: Hexadecimal id of the message (mongo object id)
        :return: array list of ClientResponse object
        """
        return self.message_dao.get_one(msg_id)

    def get_all(self):
        """
        :return: array list of ClientResponse object
        """
        return self.message_dao.get_all()

    def delete_one(self, msg_id):
        """

        :param msg_id: Hexadecimal id of the message (mongo object id)
        :return: ClientResponse object
        """
        return self.message_dao.delete_one(msg_id)

    def delete_all(self):
        """

        :return: ClientResponse object
        """
        return self.message_dao.delete_all()

    def update_one(self, msg_id, new_payload):
        """

        :param msg_id: Hexadecimal id of the message (mongo object id)
        :param new_payload:
        :return:
        """
        return self.message_dao.update_one(msg_id, new_payload)

    def pull(self):
        """

        :return: ClientResponse object
        """
        return self.message_queue_dao.pull()

    def push(self, message):
        """

        :param message: SciroccoMessage
        :return: ClientResponse object
        """
        self.message_validator.check(message)
        return self.message_queue_dao.push(message)

    def ack(self, msg_id):
        """

        :param msg_id: An hexadecimal mongo ObjectId.
        :return: ClientResponse object
        """
        return self.message_queue_dao.ack(msg_id)

    def on_receive(self, callback, async=False, request_interval=0.5):

        """
        :param callback: Function
        :param async: boolean
        :param request_interval: mixed (float or integer)
        :return: mixed (None or thread object is invocation is async)
        """
        if not callable(callback):
            raise TypeError

        if len(inspect.signature(callback).parameters) < 2:
            raise SciroccoInvalidOnReceiveCallBackError(
                "Callback must have 2 params, first for ack function, second for received message.")

        on_receive_thread = ClientOnReceiveThread(self, callback, request_interval)
        on_receive_thread.start()

        if async:
            return on_receive_thread
        else:
            on_receive_thread.join()


class ClientOnReceiveThread(Thread):
    def __init__(self, client, callback, interval):
        super().__init__()
        self.client = client
        self.callback = callback
        self.runner = Event()
        self.runner.set()
        self.interval = interval
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

    def shutdown(self, signal_number=None, stack_frame=None):

        self.runner.clear()

    def run(self):

        try:
            while self.runner.is_set():
                pulled_message = self.client.pull()
                if pulled_message:
                    self.callback(self.client, pulled_message)
                time.sleep(self.interval)

        except SciroccoInterruptOnReceiveCallbackError:
            self.shutdown()
        except KeyboardInterrupt:
            self.shutdown()
        except TypeError:
            self.shutdown()
