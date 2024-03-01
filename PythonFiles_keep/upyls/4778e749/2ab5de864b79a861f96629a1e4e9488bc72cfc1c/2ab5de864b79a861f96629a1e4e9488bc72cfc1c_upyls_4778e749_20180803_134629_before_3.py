import unittest

from limited_list import LimitedList


class MyTestCase(unittest.TestCase):
    def test_init_negative(self):
        with self.assertRaises(ValueError):
            LimitedList(limit=-3)

    def test_init_too_big(self):
        with self.assertRaises(OverflowError):
            LimitedList([i for i in range(4)], limit=3)

    def test_add(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], limit=3)
        with self.assertRaises(OverflowError):
            limited_list + 3

    def test_iadd(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], limit=3)
        with self.assertRaises(OverflowError):
            limited_list += [3]

    def test_append(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], limit=3)
        with self.assertRaises(OverflowError):
            limited_list.append(3)

    def test_insert(self):
        limited_list: LimitedList[int] = LimitedList([1, 2, 4], limit=3)
        with self.assertRaises(OverflowError):
            limited_list.insert(2, [3])

    def test_extend(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], limit=3)
        with self.assertRaises(OverflowError):
            limited_list.extend([3])


if __name__ == '__main__':
    unittest.main()
