import unittest
import inspect
import os
from icy import _path_to_objs

class TestPathToObjs(unittest.TestCase):
    def setUp(self):
        self._path_to_objs = _path_to_objs
        self.__file__ = os.path.abspath(inspect.getfile(inspect.currentframe()))
        self.test_folder = os.path.join(os.path.dirname(self.__file__), 'test_folder')

    def test_path_to_objs_file(self):
        path = self.__file__
        self.assertEqual([self.__file__], self._path_to_objs(path))
    
    def test_path_to_objs_file_glob(self):
        path = self.__file__[:-2] + '*'
        self.assertEqual([self.__file__], self._path_to_objs(path))
    
    def test_path_to_objs_folder(self):
        path = self.test_folder
        self.assertEqual([os.path.join(self.test_folder, f) for f in \
            ['1.csv', '1.txt', '2.csv', '2.txt']], self._path_to_objs(path))

    def test_path_to_objs_folder_include(self):
        path = self.test_folder
        include = ['*.csv', '*.txt']
        self.assertEqual([os.path.join(self.test_folder, f) for f in \
            ['1.csv', '1.txt', '2.csv', '2.txt']], \
            self._path_to_objs(path, include=include))

    def test_path_to_objs_folder_include_csv(self):
        path = self.test_folder
        include = ['*.csv']
        self.assertEqual([os.path.join(self.test_folder, f) for f in \
            ['1.csv', '2.csv']], \
            self._path_to_objs(path, include=include))

    def test_path_to_objs_folder_exclude_none(self):
        path = self.test_folder
        self.assertEqual([os.path.join(self.test_folder, f) for f in \
            ['.1.csv', '1.csv', '1.txt', '2.csv', '2.txt', '_1.txt']], \
            self._path_to_objs(path, exclude=[]))
    
    def test_path_to_objs_folder_exclude_hidden_1(self):
        path = self.test_folder
        exclude = ['.*']
        self.assertEqual([os.path.join(self.test_folder, f) for f in \
            ['1.csv', '1.txt', '2.csv', '2.txt', '_1.txt']], \
            self._path_to_objs(path, exclude=exclude))

    def test_path_to_objs_folder_exclude_hidden_2(self):
        path = self.test_folder
        include = ['*']
        self.assertEqual([os.path.join(self.test_folder, f) for f in \
            ['1.csv', '1.txt', '2.csv', '2.txt']], \
            self._path_to_objs(path, include=include))
    
if __name__ == '__main__':
    unittest.main()