from inspect import Parameter
import inspect
import itertools


def configurable(_fct=None, *, conf_arg='conf', path=None, forward_conf=False):
    """
    :param forward_conf:
    :param conf_arg:
    :param parameters:
    :param _fct:
    :param path: 
    :return: 
    """

    def wrap(fct):
        return _process_fct(fct, conf_arg, path, forward_conf)

    # See if we're being called as @decorator or @decorator().
    if _fct is None:
        # We're called with parens.
        return wrap

    # We're called as @decorator without parens.
    return wrap(_fct)


def _process_fct(fct, conf_argname, path, forward_conf):


    sig = inspect.signature(fct)
    param = sig.parameters.values()

    kw_param = [p.name for p in param if p.kind == p.KEYWORD_ONLY]
    pos_param = [p.name for p in param if p.kind == p.POSITIONAL_OR_KEYWORD]

    def configurated_fct(*args, **kwargs):
        if args:
            conf, *args = args
        elif conf_argname in kwargs:
            conf = kwargs[conf_argname]
        else:
            raise TypeError(f"missing argument '{conf_argname}'")

        if forward_conf:
            kwargs[conf_argname] = conf

        if path and conf:
            for subpth in path.split('/'):
                conf = conf[subpth]

        conf_kwargs = {k: v for k, v in conf.items() if k in itertools.chain(kw_param, pos_param)}

        override_args, override_kwargs = {}, {}

        # Split the fct positional arg and the *args
        args, fct_args = args[:len(pos_param)], args[len(pos_param):]

        # Map possible positionl args
        for i, arg in enumerate(args):
            override_args[pos_param[i]] = arg

        # Handle kwargs config overriding
        for key, arg in kwargs.items():
            if key in override_args:
                raise TypeError(f"got multiple values for argument '{key}'")
            else:
                override_kwargs[key] = arg

        fct_kwargs = {**conf_kwargs, **override_args, **override_kwargs}

        # Bind and call the fonction
        bind_arg = sig.bind(*fct_args, **fct_kwargs)
        bind_arg.apply_defaults()
        return fct(*bind_arg.args, **bind_arg.kwargs)

    configurated_fct.__signature__ = sig

    return configurated_fct
