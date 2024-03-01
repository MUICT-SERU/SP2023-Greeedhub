class BaseDriver(object):
    def __init__(self):
        self._history = []

    def convert_entity_parse_tree(self, entity, parse_tree):
        """Convert the entity and relationships defined by the parse_tree format"""
        pass

    def convert_entity_tree(self, entity):
        """Convert the entity and relationships associated with this entity"""
        pass

    def convert_entity(self, entity):
        """Convert an entity and return its' schema"""
        pass

    def convert_field(self, field):
        """Convert a field and return its' property schema"""
        pass
