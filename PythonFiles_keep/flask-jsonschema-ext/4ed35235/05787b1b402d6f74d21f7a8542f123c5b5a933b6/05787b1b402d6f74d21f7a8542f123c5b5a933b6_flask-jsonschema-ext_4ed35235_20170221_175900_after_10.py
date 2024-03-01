class BaseDriver(object):
    def __init__(self):
        self._history = []

    def convert_entity_tree(self, entity, tree=None, parse_tree=None):
        """Convert the entity and relationships associated with this entity"""
        pass

    def convert_entity(self, entity):
        """Convert an entity and return its' schema"""
        pass

    def convert_field(self, field):
        """Convert a field and return its' property schema"""
        pass
