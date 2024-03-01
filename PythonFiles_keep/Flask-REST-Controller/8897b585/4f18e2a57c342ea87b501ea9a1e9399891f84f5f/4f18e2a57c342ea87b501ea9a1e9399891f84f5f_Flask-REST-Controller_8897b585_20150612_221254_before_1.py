# coding: utf-8

from collections import namedtuple

__all__ = ['Router', 'convert_routing_module', 'import_module_by_string', 'set_routing']

# add router class
Router = namedtuple('Router', ['url', 'import_path', 'endpoint'])


def convert_routing_module(view_datas):
    return [Router(url=data[0], import_path=data[1], endpoint=data[2]) for data in view_datas]


def import_module_by_string(name):
    module_name, object_name = name.rsplit('.', 1)

    module = __import__(module_name)
    return getattr(module, object_name)


def set_routing(app, view_data):
    """
    apply the routing configuration you've described

    example:
        view_data = [
            ("/", "app.IndexController", "index"),
        ]

        1. "/" is receive request path
        2. "app.IndexController" is to process the received request controller class path
        3. "index" string To generate a URL that refers to the application
    """

    routing_modules = convert_routing_module(view_data)

    for module in routing_modules:
        view = import_module_by_string(module.import_path)
        app.add_url_rule(module.url, view_func=view.as_view(module.endpoint))
