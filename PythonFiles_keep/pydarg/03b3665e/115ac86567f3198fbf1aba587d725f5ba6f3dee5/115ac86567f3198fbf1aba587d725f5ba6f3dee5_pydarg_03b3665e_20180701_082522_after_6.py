import enum


class ArgType(enum.Enum):
    POSITIONAL = 0
    KEY_WORD = 1
    BOTH = 2


def extract_params(name, arg_type, args, kwargs):
    try:
        if arg_type == ArgType.BOTH:
            return kwargs.pop(name, None) or args.pop(0)
        if arg_type == ArgType.KEY_WORD:
            return kwargs.pop(name)
        if arg_type == ArgType.POSITIONAL:
            return args.pop(0)
    except IndexError or KeyError:
        return None


def get_from_path(dct, path):
    for subpth in path.split('/'):
        dct = dct[subpth]
    return dct


def verify_config(arg_type, name, forwardable, path=None, **rest):
    if rest:
        raise TypeError("'%s' is an invalid argument for this function" % rest.keys())
    if forwardable and type(forwardable) != bool:
        raise TypeError(forwardable)
    if arg_type and type(arg_type) != ArgType:
        raise TypeError(arg_type)
    if name and type(name) != str:
        raise TypeError(name)
    if path and type(path) != str:
        raise TypeError(path)
