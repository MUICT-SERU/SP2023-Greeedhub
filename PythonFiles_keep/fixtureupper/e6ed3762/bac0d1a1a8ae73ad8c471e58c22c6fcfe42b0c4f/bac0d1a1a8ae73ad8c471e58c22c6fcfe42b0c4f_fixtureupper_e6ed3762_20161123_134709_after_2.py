def inherit(relation, inherited_relation=None):
    def inherit_fn(self, fixture, k):
        related_fixture = getattr(fixture, relation, None)
        return related_fixture and getattr(related_fixture, inherited_relation or k, None)

    return inherit_fn
