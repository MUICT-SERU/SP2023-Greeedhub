#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command classes
"""

import logging
import time
import math
from .. import PARAMETER_STATUS, PARAMETER_STANDBY, PARAMETER_DOWN, \
    PARAMETER_OFF, PARAMETER_ON, PARAMETER_UP, COMMAND_POWER, COMMAND_MUTE, \
    COMMAND_MASTER_VOLUME

__logger__ = logging.getLogger(__name__)


class CommandBase(object):
    """
    Command base class.
    All other command classes should inherit from it.
    """

    command = None

    def __init__(self, denon_avr, command=None):
        self._denon_avr = denon_avr
        if command:
            self.command = command

    def send(self, parameter):
        """
        Send the class command with the given parameter
        :param parameter: Parameter to be sent
        :return: Response
        :rtype: str
        """
        return self._denon_avr.send_command(self.command, parameter)

    def status(self):
        """
        Return the status of the command.
        :return: Response
        :rtype: str
        """
        return self.send(PARAMETER_STATUS)

    def _extract_parameter(self, message):
        """
        Extract the parameter part of a message.
        :param message: Complete message
        :type message: str
        :return: Parameter
        :rtype: str
        """
        return message.replace(self.command, '').rstrip("\r")


class OnOffCommandBase(CommandBase):
    """
    Base class implementing on/off controls.
    """

    def on(self):
        """Send on control."""
        # pylint: disable=invalid-name
        return self.send(PARAMETER_ON)

    def off(self):
        """Send off control."""
        return self.send(PARAMETER_OFF)


class PowerCommand(CommandBase):
    """Control the power."""

    command = COMMAND_POWER

    def on(self):
        """Switch power on."""
        # pylint: disable=invalid-name
        response = self.send(PARAMETER_ON)
        time.sleep(1)
        return response

    def standby(self):
        """Switch power off."""
        return self.send(PARAMETER_STANDBY)


class VolumeCommand(CommandBase):
    """Control the volume."""

    command = COMMAND_MASTER_VOLUME

    ZERO_LEVEL = 80
    MINIMUM_LEVEL = 99

    def up(self):
        """Increase the volume."""
        # pylint: disable=invalid-name
        return self.send(PARAMETER_UP)

    def down(self):
        """Decrease the volume."""
        return self.send(PARAMETER_DOWN)

    def set(self, volume=0.0):
        """
        Set the volume to a given value.
        :param volume: Wanted volume in dB
        :type volume: float
        :return: Response
        :rtype: str
        """
        return self.send(self._convert_from_db(volume))

    def minimum(self):
        """Set the volume to the minimum."""
        return self.send(self.MINIMUM_LEVEL)

    def status(self):
        """
        Get the actual volume.
        :return: Volume in dB
        :rtype: float
        """
        status = super(VolumeCommand, self).status()
        return self._convert_to_db(int(self._extract_parameter(status)))

    def _convert_from_db(self, volume):
        """
        Convert the volume value from dB to parameter value.
        :param volume: Volume to be converted
        :type volume: float
        :return: Converted value
        :rtype: int
        """
        # pylint: disable=line-too-long
        steps = int(math.floor(volume / 0.5))  # Calculate the number of 0.5dB steps
        level = self.ZERO_LEVEL * 10 + (steps * 5)  # Normalize ZERO_LEVEL to be 3 digits long and add the number of steps
        level = level if level % 10 else level / 10  # Normalize level to be 2 digits long if being a 1dB value
        return level

    def _convert_to_db(self, level):
        """
        Convert a volume value to dB
        :param level: Parameter volume value to be converted
        :type level: int
        :return: Volume in dB
        :rtype: float
        """
        level = level if level / 100 > 1 else level * 10  # Normalize level if not with 3 digits
        steps = (level - self.ZERO_LEVEL * 10) / 5  # Calculate the number of 0.5dB steps
        return 0.0 + (steps * 0.5)


class MuteCommand(OnOffCommandBase):
    """Control mute."""
    command = COMMAND_MUTE


class ZoneCommand(OnOffCommandBase):
    """Control a zone."""
    pass
