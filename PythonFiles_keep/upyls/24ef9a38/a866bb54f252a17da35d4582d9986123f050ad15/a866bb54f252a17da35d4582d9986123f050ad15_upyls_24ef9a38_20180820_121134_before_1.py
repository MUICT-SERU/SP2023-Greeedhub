import unittest

from upyls import UnitOfWorkMixin


class MyUnitOfWork(UnitOfWorkMixin):

    def __init__(self):
        super(MyUnitOfWork, self).__init__()
        self.an_attribute: str = None
        self.another_attribute = "Test"


class TestUnitOfWork(unittest.TestCase):
    def test_existing_atrribute(self):
        uow = MyUnitOfWork()
        self.assertFalse(uow.is_dirty("an_attribute"))
        uow.an_attribute = "Test"
        self.assertTrue(uow.is_dirty("an_attribute"))

    def test_old_value(self):
        uow = MyUnitOfWork()
        uow.an_attribute = "Test"
        self.assertEqual(uow.old_value("an_attribute"), None)
        uow.an_attribute = "Next"
        self.assertEqual(uow.old_value("an_attribute"), "Test")

    def test_get_attribute_name(self):
        uow = MyUnitOfWork()
        self.assertEqual(uow.get_attribute_name(uow.another_attribute), "another_attribute")

    def test_get_dirty_attributes_names(self):
        uow = MyUnitOfWork()
        uow.an_attribute = "Test"
        uow.another_attribute = "Next"
        self.assertEqual(["an_attribute", "another_attribute"], uow.get_dirty_attributes_names())

    def test_get_dirty_attributes(self):
        uow = MyUnitOfWork()
        uow.an_attribute = "Test"
        uow.another_attribute = "Next"
        self.assertEqual({"an_attribute": {"old_value": None, "new_value": "Test"},
                           "another_attribute": {"old_value": "Test", "new_value": "Next"}},
                          uow.get_dirty_attributes())

    def test_commmit(self):
        uow = MyUnitOfWork()
        uow.an_attribute = "Test"
        uow.commit()
        self.assertFalse(uow.is_dirty("an_attribute"))

    def test_rollback(self):
        uow = MyUnitOfWork()
        uow.an_attribute = "Test"
        uow.rollback()
        self.assertEquals(None, uow.an_attribute)
        self.assertFalse(uow.is_dirty("an_attribute"))


if __name__ == '__main__':
    unittest.main()
