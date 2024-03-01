from ConfigWrapper import ConfigDecorator
from util import ArgType


def conf_arg(_fct=None, *, arg_type=ArgType.BOTH, name='conf', path=None, forwardable=False):
    """
    :param _fct:
    :param arg_type:
    :param name:
    :param forwardable:
    :param path:
    :return:
    """

    def wrap(fct):
        wrapper = fct if type(fct) == ConfigDecorator else ConfigDecorator(fct)
        wrapper.add_config({
            'arg_type': arg_type,
            'name': name,
            'path': path,
            'forwardable': forwardable,

        })
        return wrapper

    # See if we're being called as @decorator or @decorator().
    if _fct is None:
        # We're called with parens.
        return wrap

    # We're called as @decorator without parens.
    return wrap(_fct)
