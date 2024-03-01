import unittest

from upyls import LimitedList


class MyTestCase(unittest.TestCase):
    def test_init_negative(self):
        with self.assertRaises(ValueError):
            LimitedList(upper_limit=-3)

    def test_init_too_big(self):
        with self.assertRaises(OverflowError):
            LimitedList([i for i in range(4)], upper_limit=3)

    def test_init_too_small(self):
        with self.assertRaises(OverflowError):
            LimitedList([i for i in range(4)], lower_limit=5)

    def test_add(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], upper_limit=3)
        with self.assertRaises(OverflowError):
            limited_list + 3

    def test_iadd(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], upper_limit=3)
        with self.assertRaises(OverflowError):
            limited_list += [3]

    def test_append(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], upper_limit=3)
        with self.assertRaises(OverflowError):
            limited_list.append(3)

    def test_insert(self):
        limited_list: LimitedList[int] = LimitedList([1, 2, 4], upper_limit=3)
        with self.assertRaises(OverflowError):
            limited_list.insert(2, [3])

    def test_extend(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], upper_limit=3)
        with self.assertRaises(OverflowError):
            limited_list.extend([3])

    def test_remove(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], lower_limit=3)
        with self.assertRaises(OverflowError):
            limited_list.remove(2)

    def test_pop(self):
        limited_list: LimitedList[int] = LimitedList([i for i in range(3)], lower_limit=3)
        with self.assertRaises(OverflowError):
            limited_list.pop(1)


if __name__ == '__main__':
    unittest.main()
