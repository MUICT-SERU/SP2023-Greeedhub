import inspect
import itertools

from util import extract_params, verify_config, get_from_path


class ConfigDecorator:
    """
    Decorator that allow to handle config dictionary more easily.
    Represented as a method with attributes
    """

    def __init__(self, fct):
        self.fct = fct
        self.fct_signature = inspect.signature(fct)

        param = self.fct_signature.parameters.values()

        self.fct_kw = [p.name for p in param if p.kind == p.KEYWORD_ONLY]
        self.fct_pos = [p.name for p in param if p.kind == p.POSITIONAL_OR_KEYWORD]
        self.configs = {}

    def add_config(self, config):
        verify_config(**config)
        self.configs[config['name']] = config

    def __call__(self, *args, **kwargs):

        res_args, res_kwargs = [], {}

        for config in self.configs.values():
            cur_args, cur_kwargs = self.get_bindings(config, list(args), kwargs)
            res_args += cur_args
            res_kwargs = {**cur_kwargs, **res_kwargs}

        bind = self.fct_signature.bind(*res_args, **res_kwargs)
        bind.apply_defaults()

        return self.fct(*bind.args, **bind.kwargs)

    def get_bindings(self, config, args, kwargs):
        """
        Fetch the appropriate binding based  a specific config args

        todo:: the forward give the whole config, should it give only the small on
        todo:: name_translation

        :param config:
        :param args:
        :param kwargs:
        :return: call args, call kwargs
        """
        conf_params = extract_params(config['name'], config['arg_type'], args, kwargs)
        if config['forwardable']:
            kwargs[config['name']] = conf_params

        if config['path'] and conf_params:
            conf_params = get_from_path(conf_params, config['path'])

        if conf_params:
            valid_kwargs = self.filter_kwargs(kwargs, config['name'])
            return self.make_call_params(args, valid_kwargs, conf_params)

        else:
            return args, kwargs

    def make_call_params(self, args, kwargs, conf_arg):
        args, call_args = args[:len(self.fct_pos)], args[len(self.fct_pos):]
        conf_kwargs = {k: v for k, v in conf_arg.items() if k in itertools.chain(self.fct_kw, self.fct_pos)}

        return call_args, self.make_call_kwargs(args, kwargs, conf_kwargs)

    def make_call_kwargs(self, args, kwargs, conf_kwargs):
        # Map possible positionl args
        mapped_args = {}

        for i, arg in enumerate(args):
            mapped_args[self.fct_pos[i]] = arg

        for invalid_kwarg in (k for k in kwargs if k in mapped_args):
            raise TypeError("got multiple values for argument '%s'" % invalid_kwarg)

        return {**conf_kwargs, **mapped_args, **kwargs}

    def filter_kwargs(self, kwargs, cur_config):
        return {k: v for k, v in kwargs.items() if k == cur_config or k not in self.configs}
