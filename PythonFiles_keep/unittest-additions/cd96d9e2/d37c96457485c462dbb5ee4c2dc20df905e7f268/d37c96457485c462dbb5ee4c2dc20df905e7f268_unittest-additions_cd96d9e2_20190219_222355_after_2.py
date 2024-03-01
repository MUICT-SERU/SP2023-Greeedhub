import os
from unittest import TestCase
from unittest.mock import Mock, patch, mock_open

from unittest_additions import add_line_iter_to_mock_open


class MockOpenLineIterTestCase(TestCase):
    @patch('builtins.open', new_callable=mock_open,
        read_data='some data 0\nsome data 1\nsome data 2')
    def test_function_adds_line_iter_to_mocked_open(self, open_mock):
        EXPECTED_LINES = ['some data 0\n', 'some data 1\n', 'some data 2']

        add_line_iter_to_mock_open(open_mock)

        lines = list()
        with open('fubar', 'r') as f:
            for l in f:
                lines.append(l)

        self.assertEqual(EXPECTED_LINES, lines)
