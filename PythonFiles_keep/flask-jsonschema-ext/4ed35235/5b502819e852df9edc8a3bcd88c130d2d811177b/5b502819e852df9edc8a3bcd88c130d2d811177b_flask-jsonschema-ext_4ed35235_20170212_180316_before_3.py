class BaseDriver(object):
    @classmethod
    def convert_entity_tree(cls, entity):
        """Convert the entity and relationships associated with this entity"""
        pass

    @classmethod
    def convert_entity(cls, entity):
        """Convert an entity and return its' schema"""
        pass

    @classmethod
    def convert_field(cls, field):
        """Convert a field and return its' property schema"""
        pass
