# coding=utf-8

from functools import partial
import os.path
import unittest

import pep8

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


class TestPep8(unittest.TestCase):
    CHECKED_PATHS = ('lxml_asserts', 'tests', 'setup.py')

    def test_pep8(self):
        pep8style = pep8.StyleGuide(
            show_pep8=False,
            show_source=True,
            max_line_length=120
        )
        result = pep8style.check_files(map(partial(os.path.join, PROJECT_ROOT), TestPep8.CHECKED_PATHS))
        self.assertEqual(result.total_errors, 0, 'Pep8 found code style errors or warnings')
