#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from denonavr3312 import DenonAVR
from denonavr3312 import COMMAND_POWER, PARAMETER_ON, PARAMETER_STANDBY


class TestPowerCommand(unittest.TestCase):

    def setUp(self):
        self._denon_avr = DenonAVR(None)

    def test_on(self):
        """Test powering on."""
        self._denon_avr.send_command = MagicMock(return_value=None)
        self._denon_avr.power.on()
        self._denon_avr.send_command.assert_called_with(COMMAND_POWER, PARAMETER_ON)

    def test_standby(self):
        """Test putting in standby."""
        self._denon_avr.send_command = MagicMock(return_value=None)
        self._denon_avr.power.standby()
        self._denon_avr.send_command.assert_called_with(COMMAND_POWER, PARAMETER_STANDBY)
