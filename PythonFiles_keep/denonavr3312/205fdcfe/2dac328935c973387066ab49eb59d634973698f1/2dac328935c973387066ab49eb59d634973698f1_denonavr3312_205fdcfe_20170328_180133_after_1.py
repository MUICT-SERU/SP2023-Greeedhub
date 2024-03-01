#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from denonavr3312 import DenonAVR
from denonavr3312 import COMMAND_MUTE, PARAMETER_ON, PARAMETER_OFF


class TestMuteCommand(unittest.TestCase):

    def setUp(self):
        self._denon_avr = DenonAVR(None)

    def test_on(self):
        """Test mute on."""
        self._denon_avr.send_command = MagicMock(return_value=None)
        self._denon_avr.mute.on()
        self._denon_avr.send_command.assert_called_with(COMMAND_MUTE, PARAMETER_ON)

    def test_off(self):
        """Test mute off."""
        self._denon_avr.send_command = MagicMock(return_value=None)
        self._denon_avr.mute.off()
        self._denon_avr.send_command.assert_called_with(COMMAND_MUTE, PARAMETER_OFF)
