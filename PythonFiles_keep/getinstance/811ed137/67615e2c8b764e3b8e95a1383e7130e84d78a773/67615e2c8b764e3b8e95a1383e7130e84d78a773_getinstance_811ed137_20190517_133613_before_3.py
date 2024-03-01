
from weakref import WeakSet


class InstanceManager:
    def __init__(self, owner=None, name=None):
        """
        owner should be provided if you want to add this manager dynamically 
        to the owner class.
        """
        if owner:
            self.__set_name__(owner, name)

    def get(self, **kwargs):
        for instance in getattr(self.owner, self.weakset):
            match = True
            for attr in kwargs:
                if not hasattr(instance, attr) or \
                   not getattr(instance, attr) == kwargs[attr]:
                    match = False
                    break
            if match:
                return instance

    def all(self):
        return getattr(self.owner, self.weakset)
    
    def filter(self, **kwargs):
        for instance in getattr(self.owner, self.weakset):
            if all(getattr(instance, x) == kwargs[x] for x in kwargs):
                yield instance

    def __set_name__(self, owner_class, name):
        """
        Called at the time the owning class `owner_class` is created. The InstanceManager 
        instance has been assigned to `name`.
        """
        assert owner_class and name
        self.weakset = f'_{name}_weakset'
        if hasattr(owner_class, self.weakset):
            return

        setattr(owner_class, self.weakset, WeakSet())
        self.owner = owner_class

        # Override owner class __new__ method so that each time
        # new instance is created, it is added to the `_instances`
        __new_original__ = getattr(owner_class, '__new__', None)
        
        def __new_wrapped__(cls, *args, **kwargs):
            if __new_original__ == object.__new__:
                instance = __new_original__(cls)
            else:
                instance = __new_original__(cls, *args, **kwargs)
            getattr(cls, self.weakset).add(instance)
            return instance
        
        owner_class.__new__ = __new_wrapped__

 
