#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch

from denonavr3312 import DenonAVR


class TestDenonAVR(unittest.TestCase):

    @patch('telnetlib.Telnet', create=True)
    def test_with_usage(self, mock_telnet):
        """Test that DenonAVR class works well with with statement."""
        with DenonAVR('test') as denon_avr:
            pass
        self.assertEqual(denon_avr._conn.close.call_count, 1, 'Telnet close never called')