#import logging
from weakref import WeakSet
#from loguru import logger
#logger = logging.getLogger('getinstance')

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
        return ProxyInstances(self)
    
    def filter(self, **kwargs):
        return ProxyInstances(self, kwargs)

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
        # new instance is created, it is added to the weakset
        __new_original__ = getattr(owner_class, '__new__', None)
        
        def __new_wrapped__(cls, *args, **kwargs):
            if __new_original__ == object.__new__:
                instance = __new_original__(cls)
            else:
                instance = __new_original__(cls, *args, **kwargs)
            getattr(cls, self.weakset).add(instance)
            return instance
        
        owner_class.__new__ = __new_wrapped__

class ProxyInstances:
    def __init__(self, manager, filter=None):
        self._manager = manager
        self._filter = filter
        
    def _check_filter(self, instance):
        if self._filter:
            for pattern, value in self._filter.items():
                current = instance
                for attr in pattern.split('__'):
                    current = getattr(current, attr)
                if not current == value:
                    return False
        return True
    
    def __iter__(self):
        weakset = getattr(self._manager.owner, self._manager.weakset)
        
        for instance in list(weakset):
            if self._filter and not self._check_filter(instance):
                continue
            if instance in weakset:  # instance could have been pruned during iteration
                yield instance
        
    def __getattribute__(self, name):
        if name.startswith('_') or name in self.__dict__:
            return super().__getattribute__(name)
        return ProxyMethod(self, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in self.__dict__:
            return super().__setattr__(name, value)
        for instance in self:
            setattr(instance, name, value)
        
        
class ProxyMethod:
    def __init__(self, instances, name):
        self.instances = instances
        self.name = name
        
    def __call__(self, *a, **kw):
        for instance in self.instances:
            getattr(instance, self.name)(*a, **kw)
            
            
    
