import unittest

from upyls.config_parser import MultiIniParser


class TestMultiIniParser(unittest.TestCase):
    def test_simple_ini_config(self):
        ini_config = """ option1 = first option
        [section1]
        option2 = second option
        """
        parser = MultiIniParser()
        parser.read(ini_config)
        self.assertEqual("first option", parser[None][0]["option1"][0])



if __name__ == '__main__':
    unittest.main()
