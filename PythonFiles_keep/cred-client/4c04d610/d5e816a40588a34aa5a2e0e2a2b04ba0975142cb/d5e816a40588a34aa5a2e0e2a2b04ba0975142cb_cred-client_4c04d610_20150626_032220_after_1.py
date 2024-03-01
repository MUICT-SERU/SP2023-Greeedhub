"""
Basic example of a client using the cred.client library to perform actions on
the API server.

"""
import time
import random
import logging
from cred.client import ClientBase

# The interval at which to pull for updates from the thermostat (seconds)
pull_interval = 5

# Configure the client application
hostname = 'http://demo.codetalk.io:5000'
apikey = 'M24axXMSF8ARFRWwBQHntndeROJFqZic8WDepmwBV84'
device = 'Thermostat'
location = 'Living Room'
subscribe = {
    'Alarm': {},
    'Light': {'location': 'Living Room'}
}


class ThermostatClient(ClientBase):
    """
    An example of a thermostat client. It uses the get_temperature method to get
    the temperature from the thermostat, and set_temperature to set a new
    temperature.

    In handle_event it specifies how to handle different events.

    """

    def __init__(self, *args, **kwargs):
        # Internal temperature variable
        self._temperature = 25
        # Pass the arguments to the superclass
        super(ThermostatClient, self).__init__(*args, **kwargs)

    def set_temperature(self, value):
        """Talk to the Thermostat and set the temperature here."""
        # If the temperature is changed, submit an event to the server
        if value != self._temperature:
            self._temperature = value
            self.submit_event('Temperature', 'Changed', str(value))
            logging.info(
                'Setting Thermostat to {0} degrees'.format(value)
            )

    def get_temperature(self):
        """Talk to the Thermostat and get the temperature here."""
        # Fake a random temperature change
        temperature = random.randint(20, 25)
        self.set_temperature(temperature)

    def handle_event(self, event):
        """
        The thermostat reacts events from two devices: Light and Alarm.

        If the light is turned on in the room, then it turns up the temperature.
        This is based on the assumption that the light is only on if the room is
        in use. If the light is turned off, then temperature is lowered, because
        the room is not in use anymore.

        If the alarm clock is set off, then it turns up the temperature. This is
        based on the assumption that the room will be used shortly after.

        """
        if event['name'] == 'Light' and event['action'] == 'Toggled':
            # If the light in in the living room is turned on, change the
            # temperature
            if event['value'] == 'On':
                self.set_temperature(25)
            else:
                self.set_temperature(20)
        elif event['name'] == 'Alarm' and event['action'] == 'Alarm':
            if event['value'] == 'On':
                self.set_temperature(25)


# Instantiate, authenticate and start pulling for events
client = ThermostatClient(hostname, apikey, device, location, subscribe)
client.authenticate()
client.start_pulling_subscribedevents()

# Check the temperature every pull_interval seconds
while True:
    client.get_temperature()
    time.sleep(pull_interval)
