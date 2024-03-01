import os
from unittest import TestCase
from unittest.mock import Mock, patch, mock_open

from unittest_additions import RunTimer


class RunTimerTestCase(TestCase):
    @patch('time.perf_counter', side_effect=[0, 1, 2, 3])
    def test_split_and_overall_time(self, open_mock):
        with RunTimer() as t:
            t0 = t.split()
            t1 = t.split()

        t2 = t.overall()

        self.assertEqual(t0, 1)
        self.assertEqual(t1, 1)
        self.assertEqual(t2, 3)

    @patch('time.perf_counter', side_effect=[0, 1, 3, 4])
    def test_split_time(self, open_mock):
        with RunTimer() as t:
            t0 = t.split()
            t1 = t.split()

        self.assertEqual(t0, 1)
        self.assertEqual(t1, 2)

    @patch('time.perf_counter', side_effect=[0, 1])
    def test_split_and_overall_time(self, open_mock):
        with RunTimer() as t:
            pass

        t2 = t.overall()

        self.assertEqual(t2, 1)
