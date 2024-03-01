#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import math
from .. import PARAMETER_STATUS, PARAMETER_STANDBY, PARAMETER_DOWN, \
    PARAMETER_OFF, PARAMETER_ON, PARAMETER_UP, COMMAND_POWER, COMMAND_MUTE, \
    COMMAND_MASTER_VOLUME

logger = logging.getLogger(__name__)


class CommandBase(object):
    command = None

    def __init__(self, denon_avr, command=None):
        self._denon_avr = denon_avr
        if command:
            self.command = command

    def send(self, parameter):
        return self._denon_avr.send_command(self.command, parameter)

    def status(self):
        return self.send(PARAMETER_STATUS)

    def _extract_parameter(self, message):
        return message.replace(self.command, '').rstrip("\r")


class OnOffCommandBase(CommandBase):

    def on(self):
        return self.send(PARAMETER_ON)

    def off(self):
        return self.send(PARAMETER_OFF)


class PowerCommand(CommandBase):
    command = COMMAND_POWER

    def on(self):
        r = self.send(PARAMETER_ON)
        time.sleep(1)
        return r

    def standby(self):
        return self.send(PARAMETER_STANDBY)


class VolumeCommand(CommandBase):
    command = COMMAND_MASTER_VOLUME

    ZERO_LEVEL = 80
    MINIMUM_LEVEL = 99

    def up(self):
        return self.send(PARAMETER_UP)

    def down(self):
        return self.send(PARAMETER_DOWN)

    def set(self, volume=0.0):
        return self.send(self._convert_from_db(volume))

    def minimum(self):
        return self.send(self.MINIMUM_LEVEL)

    def status(self):
        status = super(VolumeCommand, self).status()
        return self._convert_to_db(int(self._extract_parameter(status)))

    def _convert_from_db(self, volume):
        steps = int(math.floor(volume / 0.5))  # Calculate the number of 0.5dB steps
        level = self.ZERO_LEVEL * 10 + (steps * 5)  # Normalize ZERO_LEVEL to be 3 digits long and add the number of steps
        level = level if level % 10 else level / 10  # Normalize level to be 2 digits long if being a 1dB value
        return level

    def _convert_to_db(self, level):
        level = level if level / 100 > 1 else level * 10  # Normalize level if not with 3 digits
        steps = (level - self.ZERO_LEVEL * 10) / 5  # Calculate the number of 0.5dB steps
        return 0.0 + (steps * 0.5)


class MuteCommand(OnOffCommandBase):
    command = COMMAND_MUTE


class ZoneCommand(OnOffCommandBase):
    pass
