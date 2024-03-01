import unittest

from verifycode.generator import Generator

class TestGenerator(unittest.TestCase):

    def test_init(self):
        g = Generator(is_hash_filename=True, code="1239128", width=12, height=2, fontsize=2)
        self.assertEqual(g.is_hash_filename, True)
        self.assertEqual(g.code,"1239128")
        self.assertEqual(g.width,12)
        self.assertEqual(g.height,2)
        self.assertEqual(g._fontsize,2)

    def test_format_savepath(self):
        g = Generator(is_hash_filename=False, code="12312")
        name = g._format_savepath(path_or_filename="./testdata")
        self.assertEqual(name, "./testdata/12312.png")

        g2 = Generator()
        name = g2._format_savepath(path_or_filename=".")
        self.assertEqual(name, "./default.png")
