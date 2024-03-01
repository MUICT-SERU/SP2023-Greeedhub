import unittest

from util import move_to_path


class TestUtil(unittest.TestCase):
    def test_get_from_path(self):
        result = {'e1': 1, 'e0': 0}
        dct = {'child': {'subchild': result}}

        self.assertEqual(result, move_to_path(dct, "child/subchild"))
        self.assertEqual(dct, move_to_path(dct, None))
        self.assertEqual(dct, move_to_path(dct, ""))


if __name__ == '__main__':
    unittest.main()
