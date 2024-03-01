#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Global classes
"""

import logging
import telnetlib
from socket import error
from .commands import PowerCommand, VolumeCommand, MuteCommand, ZoneCommand
from .. import COMMAND_MUTE, COMMAND_ZONE_2, COMMAND_ZONE_3

__logger__ = logging.getLogger(__name__)


class DenonAVR(object):
    """Base class to control Denon device, this should be the only one used."""

    COMMAND_TPL = "{cmd}{param}\r"
    RESPONSE_TIMEOUT = 0.200
    CONNECT_TIMEOUT = 10
    TELNET_PORT = 23

    def __init__(self, address):
        self._address = address
        self._conn = None

        self.power = PowerCommand(self)
        self.master_volume = VolumeCommand(self)
        self.mute = MuteCommand(self)
        self.zone2 = Zone(self, COMMAND_ZONE_2)
        self.zone3 = Zone(self, COMMAND_ZONE_3)

        self.open()

    def __repr__(self):
        return self._address

    def open(self):
        """
        Open the connection to Denon device
        :return: None
        """
        try:
            __logger__.debug('Start telnet connection to %s', self._address)
            self._conn = telnetlib.Telnet(self._address,
                                          self.TELNET_PORT,
                                          timeout=self.CONNECT_TIMEOUT)
        except error as _:  # pragma: no cover
            __logger__.error('Error when opening telnet connection: %s', _)
            raise _

    def close(self):
        """
        Close connection to Denon device
        :return: None
        """
        __logger__.debug('Close telnet connection to %s', self._address)
        self._conn.close()
        __logger__.debug('Remaining messages in the queue: %s', self._conn.read_all())

    def send_command(self, command, parameter):
        """
        Send a command to the Denon device
        :param command: Command to be send
        :param parameter: Command's parameter
        :return: Response
        :rtype: str
        """
        format_cmd = self.COMMAND_TPL.format(cmd=command, param=parameter).encode('ascii')
        self._conn.write(format_cmd)
        response = self._conn.read_until(b"\r", timeout=self.RESPONSE_TIMEOUT)
        response = response.decode('ascii')
        __logger__.debug('Response to command %s: %s',
                         format_cmd.rstrip(b"\r"),
                         response.rstrip("\r"))
        return response

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Zone(object):
    """Represent a zone, this is an internal class."""
    # pylint: disable=too-few-public-methods
    def __init__(self, denon_avr, zone_name):
        self._zone_name = zone_name
        self._denon_avr = denon_avr

        self._control = ZoneCommand(self._denon_avr, self._zone_name)
        self.volume = VolumeCommand(self._denon_avr, self._zone_name)
        self.mute = MuteCommand(self._denon_avr, self._zone_name + COMMAND_MUTE)

    def __repr__(self):
        return '%s-%s' % (self._denon_avr, self._zone_name)

    def __getattr__(self, item):
        return getattr(self._control, item)
