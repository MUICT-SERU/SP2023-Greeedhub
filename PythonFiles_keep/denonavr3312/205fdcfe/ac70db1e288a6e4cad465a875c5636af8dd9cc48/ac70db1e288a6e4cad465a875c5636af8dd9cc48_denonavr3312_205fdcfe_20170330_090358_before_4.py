#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from denonavr3312.classes.commands import VolumeCommand
from denonavr3312 import PARAMETER_UP, PARAMETER_DOWN

class TestVolumeCommand(unittest.TestCase):

    _dbs_to_levels = {
        '-45.5': '345',
        '-48': '32'
    }

    def setUp(self):
        self._volume = VolumeCommand(None, None)

    def _mock_send(self, return_value=None):
        self._volume.send = MagicMock(return_value=return_value)

    def test_convert_from_db(self):
        """Test that values in dB format are properly converted to values."""
        for (db, lvl) in self._dbs_to_levels.items():
            self.assertEqual(self._volume._convert_from_db(float(db)), int(lvl))

    def test_convert_to_db(self):
        """Test that values are properly converted to dB."""
        for (db, lvl) in self._dbs_to_levels.items():
            self.assertEqual(self._volume._convert_to_db(int(lvl)), float(db))

    def test_set(self):
        """Test volume setup."""
        self._mock_send()
        for (db, lvl) in self._dbs_to_levels.items():
            self._volume.set(float(db))
            self._volume.send.assert_called_with(int(lvl))

    def test_up(self):
        """Test increasing volume."""
        self._mock_send()
        self._volume.up()
        self._volume.send.assert_called_with(PARAMETER_UP)

    def test_down(self):
        """Test decreasing volume."""
        self._mock_send()
        self._volume.down()
        self._volume.send.assert_called_with(PARAMETER_DOWN)

    def test_minimum(self):
        """Test put volume to minimum."""
        self._mock_send()
        self._volume.minimum()
        self._volume.send.assert_called_with(self._volume.MINIMUM_LEVEL)

    def test_status(self):
        """Test getting volume."""
        for (db, lvl) in self._dbs_to_levels.items():
            self._mock_send(lvl)
            self.assertEqual(self._volume.status(), float(db))