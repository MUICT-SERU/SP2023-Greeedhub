import unittest
import os.path as path
import os
import shutil 
from verifycode.generator import Generator, CodeOverLenError

class TestGenerator(unittest.TestCase):
    
    def setUp(self):
        try:
            os.mkdir("./testcase")
            os.mkdir("./testcase/multi")
        except Exception as _:
            pass
    
    def tearDown(self):
        try:
            shutil.rmtree("./testcase", ignore_errors=True)
        except Exception as e:
            print(e)

    def test_init(self):
        g = Generator(is_hash_filename=True, width=12, height=2, fontsize=2)
        self.assertEqual(g.is_hash_filename, True)
        self.assertEqual(g.code, "")
        self.assertEqual(g.width,12)
        self.assertEqual(g.height,2)
        self.assertEqual(g._fontsize,2)

    def test_format_savepath(self):
        g = Generator(is_hash_filename=False)
        g.generate(code="12312")
        name = g._format_savepath(path_or_filename="./testcase")
        g.save(name, need_format=False)
        self.assertEqual(name, "./testcase/12312.png")

        g2 = Generator()
        name = g2._format_savepath(path_or_filename="./testcase")
        self.assertEqual(name, "./testcase/default.png")

    def test_generate(self):
        g = Generator()
        g.generate(code="237192")
        g.save("./testcase")
        self.assertTrue(path.exists("./testcase/237192.png"))

        try:
            g.generate("123172093")
        except Exception as e:
            self.assertEqual(e.__str__(), CodeOverLenError(9, 6).__str__())

    def test_generate_multi(self):
        g = Generator()
        g.generate_multi(codes=["123123","412322", "123"], folder="./testcase")