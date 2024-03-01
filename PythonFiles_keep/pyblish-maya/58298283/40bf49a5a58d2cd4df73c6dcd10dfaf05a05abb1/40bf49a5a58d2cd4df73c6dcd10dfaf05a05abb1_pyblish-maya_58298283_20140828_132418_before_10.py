import pyblish.backend.plugin

from maya import cmds


class ValidateMutedChannels(pyblish.backend.plugin.Validator):
    """Ensure no muted channels exists in scene

    Todo: Ensure no muted channels are associated with involved nodes
        At the moment, the entire scene is checked.

    """

    @property
    def families(self):
        return ['model']

    @property
    def hosts(self):
        return ['maya']

    @property
    def version(self):
        return (0, 1, 0)

    def process(self, context):
        """Look for nodes of type 'mute'"""
        mutes = cmds.ls(type='mute')
        if mutes:
            raise ValueError("Muted nodes found")

    def fix(self):
        mutes = cmds.ls(type='mute')
        cmds.delete(mutes)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
