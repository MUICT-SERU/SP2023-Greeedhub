import enum


class ArgType(enum.Enum):
    POSITIONAL = 0
    KEY_WORD = 1
    BOTH = 2


def get_dct(name, arg_type, args, kwargs):
    try:
        if arg_type == ArgType.BOTH:
            return kwargs.pop(name, None) or args.pop(0)
        if arg_type == ArgType.KEY_WORD:
            return kwargs.pop(name)
        if arg_type == ArgType.POSITIONAL:
            return args.pop(0)
    except IndexError or KeyError:
        return None


def get_from_paths(conf_args, paths):
    return {name: move_to_path(conf_args, path) for name, path in paths.items()}


def move_to_path(dct, path):
    path = path or ""
    try:
        for subpth in (p for p in path.split('/') if p):
            dct = dct[subpth]
        return dct
    except KeyError:
        raise TypeError('%s: path not found in dictionary' % path)


def verify_config(arg_type, name, path=None, **rest):
    if arg_type and type(arg_type) != ArgType:
        raise TypeError(arg_type)
    if name and type(name) != str:
        raise TypeError(name)
    if path and type(path) != str:
        raise TypeError(path)
