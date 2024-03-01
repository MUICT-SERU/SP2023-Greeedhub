#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch

from denonavr3312 import DenonAVR


class TestDenonAVR(unittest.TestCase):

    def setUp(self):

        # Mock Telnet class
        patcher = patch('telnetlib.Telnet', create=True)
        self._telnet_mock = patcher.start()
        self.addCleanup(patcher.stop)

        self._denon_avr = DenonAVR(None)
        self._denon_avr._conn.read_until.return_value = b"NOOP\r"

    @patch('telnetlib.Telnet', create=True)
    def test_with_statement(self, telnet_mock):
        """Test that DenonAVR class works well with with statement."""
        with DenonAVR(None) as denon_avr:
            pass
        self.assertEqual(denon_avr._conn.close.call_count, 1, 'Telnet close never called')

    def test_powering_on(self):
        """Test powering on."""
        self._denon_avr.power.on()
        self._denon_avr._conn.write.assert_called_with(b"PWON\r")

    def test_powering_standby(self):
        """Test putting in standby."""
        self._denon_avr.power.standby()
        self._denon_avr._conn.write.assert_called_with(b"PWSTANDBY\r")

    def test_muting_on(self):
        """Test mute on."""
        self._denon_avr.mute.on()
        self._denon_avr._conn.write.assert_called_with(b"MUON\r")

    def test_muting_off(self):
        """Test mute off."""
        self._denon_avr.mute.off()
        self._denon_avr._conn.write.assert_called_with(b"MUOFF\r")

    def test_volume_up(self):
        """Test increasing volume."""
        self._denon_avr.master_volume.up()
        self._denon_avr._conn.write.assert_called_with(b"MVUP\r")

    def test_volume_down(self):
        """Test decreasing volume."""
        self._denon_avr.master_volume.down()
        self._denon_avr._conn.write.assert_called_with(b"MVDOWN\r")

    def test_zone2_on(self):
        """Test to activate zone 2."""
        self._denon_avr.zone2.on()
        self._denon_avr._conn.write.assert_called_with(b"Z2ON\r")