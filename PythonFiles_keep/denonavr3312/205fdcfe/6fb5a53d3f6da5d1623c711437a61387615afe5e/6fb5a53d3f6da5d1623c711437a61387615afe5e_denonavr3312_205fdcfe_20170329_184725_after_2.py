#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from denonavr3312 import DenonAVR


class TestMuteCommand(unittest.TestCase):

    def setUp(self):
        patcher = patch('telnetlib.Telnet', create=True)
        self._telnet_mock = patcher.start()
        self.addCleanup(patcher.stop)
        self._denon_avr = DenonAVR(None)
        self._denon_avr._conn.read_until.return_value = b"NOOP\r"

    def test_on(self):
        """Test mute on."""
        self._denon_avr.mute.on()
        self._denon_avr._conn.write.assert_called_with(b"MUON\r")

    def test_off(self):
        """Test mute off."""
        self._denon_avr.mute.off()
        self._denon_avr._conn.write.assert_called_with(b"MUOFF\r")
