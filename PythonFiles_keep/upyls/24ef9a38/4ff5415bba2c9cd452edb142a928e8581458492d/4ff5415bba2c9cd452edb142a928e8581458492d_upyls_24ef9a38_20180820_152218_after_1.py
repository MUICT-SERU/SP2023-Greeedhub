from __future__ import annotations
from abc import ABC
from typing import Dict, Any, List


class UnitOfWorkMixin(ABC):
    """
    A mixin which makes a class provide Unit of Work functionality if you derive from it
    """
    def __init__(self):
        self.__dirty_attributes: Dict = {}

    def is_dirty(self, attribute_name) -> bool:
        """
        Checks if an attribute has been changed
        :param attribute_name: the name of the attribute to be checked
        :return: True if this attribute has been changed, False if not
        """
        if attribute_name in self.__dirty_attributes:
            if self.__dirty_attributes[attribute_name]["new"] is True:
                return False
            else:
                return True
        else:
            return False

    def old_value(self, attribute_name: str) -> Any:
        """
        query the old value before the change
        :param attribute_name: The name of the changed attribute
        :return: the old value before the change
        :raise ValueError: if this attribute has not been changed
        """
        if not self.is_dirty(attribute_name):
            raise ValueError("Attribute is not Dirty")
        return self.__dirty_attributes[attribute_name]["old_value"]

    def get_attribute_name(self, attribute_value: Any):
        """
        Query the name of the attribute by passing this attribute's value
        :param attribute_value: The attribute's value the name is queried for
        :return: the attribute's name
        """
        attr_id = id(attribute_value)
        for itemname, itemvalue in self.__dict__.items():
            if id(itemvalue) == attr_id:
                return itemname

    def get_dirty_attributes_names(self) -> [str]:
        """
        Get a the names of the attributes which have been changed
        :return: The names of the attributes
        """
        if self.__dirty_attributes == {}:
            return []
        dirty_attributes: list = []
        for attribute_name in self.__dirty_attributes.keys():
            dirty_attributes.append(attribute_name)
        return dirty_attributes

    def get_dirty_attributes(self) -> Dict[str, Dict[str, Any]]:
        """
        get all changed attributes incuding their respective old and new values
        :return: all changed attributes
        """
        if self.__dirty_attributes == {}:
            return self.__dirty_attributes
        dirty_attributes: Dict[str, Dict[str, Any]] = {}
        for attribute in self.__dirty_attributes:
            dirty_attributes[attribute] = {"old_value": self.__dirty_attributes[attribute]["old_value"],
                                           "new_value": self.__dirty_attributes[attribute]["new_value"]}
        return dirty_attributes

    def commit(self):
        self.__dict__["_UnitOfWorkMixin__dirty_attributes"] = {}

    def rollback(self):
        for attribute in self.__dirty_attributes:
            self.__dict__[attribute] = self.__dirty_attributes[attribute]["old_value"]
        self.__dict__["_UnitOfWorkMixin__dirty_attributes"] = {}

    def __setattr__(self, attribute: str, value):
        if hasattr(self, attribute):
            if self.__getattribute__(attribute) is None:
                self._dirty(attribute, False, value, None)
                self.__dict__[attribute] = value
            else:
                self._update_attribute(attribute, value)
        else:
            self._create_attribute(attribute, value)

    def _update_attribute(self, attribute_name: str, value):
        """
        Update an attribute
        :param attribute_name: the attribute's name
        :param value: the attrbie's new value
        :return:
        """
        old_value = getattr(self, attribute_name)
        self._dirty(attribute_name, False, value, old_value)
        self.__dict__[attribute_name] = value

    def _create_attribute(self, attribute: str, value):
        """
        create a new Attribute for this class
        :param attribute: the attribute's name
        :param value: the attribute's value
        """
        self.__dict__[attribute] = value

    def _dirty(self, attribute_name: str, new: bool, new_value, old_value=None):
        """
        Mark an attribute as dirty
        :param attribute_name: the attributes name
        :param new: if an attribute is newly created
        :param new_value: the attribute's updated value
        :param old_value: the attributes old value
        """
        self.__dirty_attributes[attribute_name] = {"old_value": old_value, "new_value": new_value, "new": new}


class ManageableUnitOfWorkMixin(UnitOfWorkMixin, ABC):
    """
    Extends :class UnitOfWorkMixin: with manageability. This means that this mixin is prepared to be managed by a
    :class UnitOfWorkManager: there can be multiple instances of this class be managed by a :class UnitOfWorkManager:.
    """

    def __init__(self, manager: UnitOfWorkManager=None):
        """
        Construct a manageable Unit of work mixin
        :param manager: optional, if the created instance should already be connected with a manager
        """
        super(ManageableUnitOfWorkMixin, self).__init__()
        self.__manager = manager
        if self.__manager:
            self.__manager.register(self)

    @property
    def manager(self) -> UnitOfWorkManager:
        """
        get the connected manager of this instance
        :return: the instance of the manager this class is connected with
        """
        return self.__manager

    def set_manager(self, manager: UnitOfWorkManager):
        """
        set the connected manager for this instance and register this instance with the passed manager
        :param manager: the manager this instance should be connected with
        """
        if manager is None:
            if self.__manager:
                self.__manager.unregister(self)
                self.remove_manager()
            return
        if manager is not None:
            self.__manager = manager
            if not manager.is_registered(self):
                manager.register(self)

    def remove_manager(self):
        """
        Remove the connection between this instance and its manager. Also deregisters this instance with the previously
        connected manager before removing the manager.
        """
        if self.__manager:
            self.__manager.unregister(self)
        self.__manager = None

    def commit(self):
        """
        Like the commit method of :super: the new value of dirty attributes is kept and the old value discarded.
        Additionally if this instance is connected with a manager, the manager is notified that this instance clean
        again
        """
        super(ManageableUnitOfWorkMixin, self).commit()
        if self.manager:
            self.manager.notify_clean(self)

    def rollback(self):
        """
        Like the rollback method of :super: the new value of dirty attributes is discarded and the old value restored.
        Additionally if this instance is connected with a amanger, the manager is notified that this instance is clean
        again
        """
        super(ManageableUnitOfWorkMixin, self).rollback()
        if self.manager:
            self.manager.notify_clean(self)

    def _dirty(self, attribute_name: str, new: bool, new_value, old_value=None):
        """
        Like in the dirty-method of :super: an attribute is marked as dirty. Additionally if this instance is connected
        with a manager, the manager is notified that this instance is dirty
        :param attribute_name: the name of the attribute to mark as dirty
        :param new: indicate that this attribute is a new attribute, which has not existed before
        :param new_value: the attribute's new value
        :param old_value: the attribute's old value
        """
        super(ManageableUnitOfWorkMixin, self)._dirty(attribute_name, new, new_value, old_value)
        if self.manager is not None:
            self.manager.notify_dirty(self)

    def __setattr__(self, attribute: str, value):
        if hasattr(self, attribute):
            if self.__getattribute__(attribute) is None:
                self._dirty(attribute, False, value, None)
                self.__dict__[attribute] = value
            else:
                self._update_attribute(attribute, value)
        else:
            self._create_attribute(attribute, value)
            
    def _create_attribute(self, attribute: str, value):
        super(ManageableUnitOfWorkMixin, self)._create_attribute(attribute, value)


class UnitOfWorkManager:
    """
    class for keeping track of :class UnitOfWorkMixin: objects. So instances of classes, which derive from
    :class ManageableUnitOfWorkMixin: and which are registered with an instance of this class will call the
    notify-method when they get changed.
    """
    def __init__(self):
        self.__registered_units: List[ManageableUnitOfWorkMixin] = []
        self.__dirty_units: List[ManageableUnitOfWorkMixin] = []

    def register(self, unit: ManageableUnitOfWorkMixin):
        """
        Register manageable Units of Work with this manager instance. Additionally set this instance as the unit's
        manager
        :param unit: a manageable Unit of Work to be registered
        """
        self.registered_units.append(unit)
        if unit.manager != self:
            unit.set_manager(self)

    def unregister(self, unit: ManageableUnitOfWorkMixin):
        """
        Unregister a previously registered manageable Unit of work from this manager instance. Additionally remove this
        as the unit's manager
        :param unit: the manageable Unit of work to be unregistered
        """
        self.registered_units.remove(unit)
        if unit.remove_manager == self:
            unit.remove_manager(self)

    @property
    def registered_units(self) -> List[ManageableUnitOfWorkMixin]:
        """
        Get the Units of Work, which have been registered with this instance
        :return: all Units registered with this instance
        """
        return self.__registered_units

    @property
    def dirty_units(self) -> List[ManageableUnitOfWorkMixin]:
        """
        Get the (registered) Units of Work, which have been marked as dirty
        :return:
        """
        return self.__dirty_units

    def notify_dirty(self, unit: ManageableUnitOfWorkMixin):
        """
        Notify this manager instance that a manageable Unit of Work has been changed. This method is called by instances
        :class ManageableUnitOfWorkMixin: when one of their attributes change, when those instances have got this
        instance as their manager.
        :param unit: the manageable Unit of Work that has changed
        :return:
        """
        if unit not in self.registered_units:
            raise ValueError("Unit of work is unknown")
        self.dirty_units.append(unit)

    def notify_clean(self, unit: ManageableUnitOfWorkMixin):
        """
        Notify this manager instance that a manageable Unit of Work has been either commited or rolled back and now is
        clean again
        :param unit: the manageable Unit of Work, which is clean again
        :return:
        """
        if unit not in self.registered_units:
            raise ValueError("Unit of work is unknown")
        if unit in self.dirty_units:
            self.dirty_units.remove(unit)

    def commit_dirty_units(self):
        """
        Go through all (registered) manageable Units of Work and commit their changes.
        """
        dirty_units = self.dirty_units.copy()
        for unit in dirty_units:
            unit.commit()
            if unit in self.dirty_units:
                self.dirty_units.remove(unit)

    def rollback_dirty_units(self):
        """
        Go through all (registered) manageable Units of Work and rollback their changes.
        """
        dirty_units = self.dirty_units.copy()
        for unit in dirty_units:
            unit.rollback()
            if unit in self.dirty_units:
                self.dirty_units.remove(unit)

    def is_registered(self, unit: ManageableUnitOfWorkMixin) -> bool:
        """
        Check if a manageable Unit of Work is registered with this manager instance
        :param unit:
        :return:
        """
        return unit in self.registered_units

    def is_dirty(self, unit: ManageableUnitOfWorkMixin) -> bool:
        """
        Check if a manageable Unit of Work has been marked as dirty
        :param unit: the manageable Unit of work to check
        :return: True if the unit is marked as dirty, False otherwise
        """
        return unit in self.dirty_units
