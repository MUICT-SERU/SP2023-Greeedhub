
from weakref import WeakSet


class InstanceManager:
    def __init__(self, owner=None):
        """
        owner should be provided if you want to add this manager dynamically 
        to the owner class.
        """
        if owner:
            self.__set_name__(owner, None)

    def get(self, **kwargs):
        for instance in self.owner._instances:
            match = True
            for attr in kwargs:
                if not hasattr(instance, attr) or \
                   not getattr(instance, attr) == kwargs[attr]:
                    match = False
                    break
            if match:
                return instance

    def all(self):
        return self.owner._instances


    def __set_name__(self, owner_class, name):
        """
        Called at the time the owning class `owner_class` is created. The InstanceManager 
        instance has been assigned to `name`.
        """
        if hasattr(owner_class, '_instances'):
            return

        owner_class._instances = WeakSet()
        self.owner = owner_class

        # Override owner class __new__ method so that each time
        # new instance is created, it is added to the `_instances`
        __new_original__ = getattr(owner_class, '__new__', None)
        
        def __new_wrapped__(cls, *args, **kwargs):
            if __new_original__ == object.__new__:
                instance = object.__new__(cls)
            else:
                instance = super().__new__(cls, *args, **kwargs)
            cls._instances.add(instance)
            return instance
        
        owner_class.__new__ = __new_wrapped__

 
