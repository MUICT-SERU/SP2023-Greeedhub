from DctArgWrapper import DctArgWrapper
from util import ArgType


def conf_arg(_fct=None, *, arg_type=ArgType.BOTH, name='conf', path="", fetch_args=None):
    """
    :param fetch_args:
    :param _fct:
    :param arg_type:
    :param name:
    :param path:
    :return:
    """

    def wrap(fct):
        wrapper = fct if type(fct) == DctArgWrapper else DctArgWrapper(fct)
        wrapper.add_config({
            'arg_type': arg_type,
            'name': name,
            'path': path,
            'fetch_args': fetch_args or {}
        })
        return wrapper

    # See if we're being called as @decorator or @decorator().
    if _fct is None:
        # We're called with parens.
        return wrap

    # We're called as @decorator without parens.
    return wrap(_fct)
