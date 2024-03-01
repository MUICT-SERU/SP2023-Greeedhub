#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from denonavr3312 import DenonAVR


class TestPowerCommand(unittest.TestCase):

    def setUp(self):
        patcher = patch('telnetlib.Telnet', create=True)
        self._telnet_mock = patcher.start()
        self.addCleanup(patcher.stop)
        self._denon_avr = DenonAVR(None)
        self._denon_avr._conn.read_until.return_value = b"NOOP\r"

    def test_on(self):
        """Test powering on."""
        self._denon_avr.power.on()
        self._denon_avr._conn.write.assert_called_with(b"PWON\r")

    def test_standby(self):
        """Test putting in standby."""
        self._denon_avr.power.standby()
        self._denon_avr._conn.write.assert_called_with(b"PWSTANDBY\r")
