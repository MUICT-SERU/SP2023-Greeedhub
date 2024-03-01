#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position

"""
Module to control Denon AVR device through telnet control protocol
"""

COMMAND_POWER = 'PW'
COMMAND_MUTE = 'MU'
COMMAND_MASTER_VOLUME = 'MV'
COMMAND_CHANNEL_VOLUME = 'CV'
COMMAND_CHANNEL_SETTING = 'CS'
COMMAND_SELECT_INPUT = 'SI'
COMMAND_ZONE_MAIN = 'ZM'
COMMAND_ZONE_2 = 'Z2'
COMMAND_ZONE_3 = 'Z3'
COMMAND_SELECT_REC = 'SR'
COMMAND_SELECT_VIDEO = 'SV'
COMMAND_SLEEP = 'SLP'

PARAMETER_ON = 'ON'
PARAMETER_OFF = 'OFF'
PARAMETER_STATUS = '?'
PARAMETER_STANDBY = 'STANDBY'
PARAMETER_UP = 'UP'
PARAMETER_DOWN = 'DOWN'

from .classes.avr import DenonAVR as DenonAVR  # noqa: E402,F401
