import unittest

from upyls import UnitOfWorkMixin, UnitOfWorkManager
from upyls.unit_of_work import ManageableUnitOfWorkMixin


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
        self.assertEqual(None, uow.an_attribute)
        self.assertFalse(uow.is_dirty("an_attribute"))


class ManagedUnitOfWork(ManageableUnitOfWorkMixin):

    def __init__(self, manager: UnitOfWorkManager=None):
        super(ManagedUnitOfWork, self).__init__(manager)
        self.an_attribute: str = None
        self.another_attribute = "Test"


class TestUnitOfWorkManager(unittest.TestCase):

    def test_init_manager(self):
        manager = UnitOfWorkManager()
        unit = ManagedUnitOfWork(manager)
        self.assertEqual(manager, unit.manager)
        self.assertEqual(unit, manager.registered_units[0])
        self.assertEqual([], unit.get_dirty_attributes_names())

    def test_get_registered(self):
        manager = UnitOfWorkManager()
        unit1 = ManagedUnitOfWork(manager)
        unit2 = ManagedUnitOfWork(manager)
        self.assertEqual([unit1, unit2], manager.registered_units)

    def test_get_dirty(self):
        manager = UnitOfWorkManager()
        unit = ManagedUnitOfWork(manager)
        unit.an_attribute = "Test"
        self.assertEqual(unit, manager.dirty_units[0])

    def test_commit(self):
        manager = UnitOfWorkManager()
        unit1 = ManagedUnitOfWork(manager)
        unit2 = ManagedUnitOfWork(manager)
        unit1.an_attribute = "Test1"
        unit2.an_attribute = "Test2"
        manager.commit_dirty_units()
        self.assertEqual([], manager.dirty_units)

    def test_rollback(self):
        manager = UnitOfWorkManager()
        unit1 = ManagedUnitOfWork(manager)
        unit2 = ManagedUnitOfWork(manager)
        unit1.an_attribute = "Test1"
        unit2.an_attribute = "Test2"
        manager.rollback_dirty_units()
        self.assertEqual([], manager.dirty_units)
        self.assertEqual(None, unit1.an_attribute)
        self.assertEqual(None, unit2.an_attribute)

    def test_is_registered_previously_registered(self):
        manager = UnitOfWorkManager()
        unit1 = ManagedUnitOfWork(manager)
        unit2 = ManagedUnitOfWork()
        unit3 = ManagedUnitOfWork()
        unit3.set_manager(manager)
        manager.register(unit2)
        self.assertTrue(manager.is_registered(unit1))
        self.assertTrue(manager.is_registered(unit2))
        self.assertTrue(manager.is_registered(unit3))

    def test_is_registered_previously_not_registered(self):
        manager = UnitOfWorkManager()
        unit = ManagedUnitOfWork()
        self.assertFalse(manager.is_registered(unit))

    def test_is_dirty_with_dirty_unit(self):
        manager = UnitOfWorkManager()
        unit = ManagedUnitOfWork(manager)
        unit.an_attribute = "Test"
        self.assertTrue(manager.is_dirty(unit))

    def test_is_dirty_with_clean_unit(self):
        manager = UnitOfWorkManager()
        unit = ManagedUnitOfWork(manager)
        self.assertFalse(manager.is_dirty(unit))


if __name__ == '__main__':
    unittest.main()
