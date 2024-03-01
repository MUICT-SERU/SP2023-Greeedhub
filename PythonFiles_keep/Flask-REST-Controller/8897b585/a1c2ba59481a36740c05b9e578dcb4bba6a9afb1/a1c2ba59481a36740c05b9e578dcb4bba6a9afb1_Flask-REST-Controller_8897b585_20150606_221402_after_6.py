# coding: utf-8

from collections import namedtuple

__all__ = ['Router', 'merge_routing_modules', 'import_module_by_string', 'set_routing']

# add router class
Router = namedtuple('Router', ['url', 'import_path', 'endpoint'])


def merge_routing_modules(view_datas):
    return [Router(url=data[0], import_path=data[1], endpoint=data[2]) for data in view_datas]


def import_module_by_string(name):
    module_name, object_name = name.rsplit('.', 1)

    module = __import__(module_name)
    return getattr(module, object_name)


def set_routing(app, view_data):
    routing_modules = merge_routing_modules(view_data)

    for module in routing_modules:
        view = import_module_by_string(module.import_path)
        app.add_url_rule(module.url, view_func=view.as_view(module.endpoint))
