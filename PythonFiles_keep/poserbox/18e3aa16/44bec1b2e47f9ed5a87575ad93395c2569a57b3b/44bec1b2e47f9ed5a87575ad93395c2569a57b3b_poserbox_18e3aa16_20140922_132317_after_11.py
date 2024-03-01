# -*- coding: utf-8 -*-
import os
import shutil
import unittest
import urllib2

from poserbox import PoserBox
from poserbox.nose_plugin import DEFAULT_PORT_ENVVAR


class TestPoserBox(unittest.TestCase):

    def test_nose_plugin_exports_envvar(self):
        self.assertTrue(DEFAULT_PORT_ENVVAR in os.environ)

    def test_can_run_poser(self):
        scenes_file = os.path.join(os.path.dirname(__file__),
                                   'fixtures', 'simple_get.yaml')
        box = PoserBox(scenes_file=scenes_file)
        box.play()

        self.assertTrue(box.running())
        self.assertIsNotNone(box.port)
        data = urllib2.urlopen("http://example.com/").read()
        self.assertIn("<html", data)

        box.stop()

        self.assertFalse(box.running())


if __name__ == "__main__":
    unittest.main()
