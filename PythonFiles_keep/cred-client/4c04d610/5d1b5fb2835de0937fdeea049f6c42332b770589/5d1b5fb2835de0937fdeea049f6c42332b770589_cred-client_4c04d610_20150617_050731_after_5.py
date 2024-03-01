"""
Basic example of a client using the cred.client library to perform actions on
the API server.

"""
import time
import logging
from cred.client import ClientBase


class MyClient(ClientBase):
    """Implement the handle_event method."""

    def handle_event(self, event):
        """Act on an event here."""
        logging.info(
            'Handling an event with ID {0}'.format(event['id'])
        )


# Our configuration
hostname = 'http://127.0.0.1:5000'
apikey = 'qWqa7nhoYdeJIX5FIJwb4Q4bjM79hNUF6GFh8kQt6uE'
device = 'Client Library'
location = 'Laptop'
subscribe = {
    'Temperature': {}
}

client = MyClient(hostname, apikey, device, location, subscribe)
auth = client.authenticate()
event_daemon = client.start_pulling_subscribedevents()
while True:
    # Post an event every 2 seconds
    client.submit_event('Test', 'Performing a test', 'True')
    time.sleep(2)
