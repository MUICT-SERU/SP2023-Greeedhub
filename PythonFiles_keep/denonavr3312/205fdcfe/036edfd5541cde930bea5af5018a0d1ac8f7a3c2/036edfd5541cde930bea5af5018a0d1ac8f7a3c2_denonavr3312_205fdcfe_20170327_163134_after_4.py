#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from denonavr3312.classes.commands import VolumeCommand

class TestVolumeCommand(unittest.TestCase):

    def setUp(self):
        self._volume = VolumeCommand(None, None)

    def test_convert_from_db(self):
        """Test that values in dB format are properly converted to values."""
        self.assertEqual(self._volume._convert_from_db(-45.5), 345)
        self.assertEqual(self._volume._convert_from_db(-48), 32)

    def test_convert_to_db(self):
        """Test that values are properly converted to dB."""
        self.assertEqual(self._volume._convert_to_db(345), -45.5)
        self.assertEqual(self._volume._convert_to_db(32), -48)