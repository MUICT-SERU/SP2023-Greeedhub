from importlib import import_module

import six
from django.core.urlresolvers import reverse
from django.utils.six import wraps


class MenuItem:
    _counter = 0

    def __init__(self, route=None, visibility=None, title=None, **kwargs):
        self.title = title
        self.visibility = visibility
        self.route = route
        self.kwargs = kwargs
        self._index = MenuItem._counter
        MenuItem._counter += 1
        self.items = []
        self.cached_url = False

    def activate(self, f=None, only=False, before=True):
        def actual_wrap(f):
            if isinstance(f, type):
                that = self
                old_dispatch = f.dispatch

                @wraps(old_dispatch)
                def wrapper(self, request, *args, **kwargs):
                    if before:
                        that.activate_for_request(request, only)

                    result = old_dispatch(self, request, *args, **kwargs)

                    if not before:
                        that.activate_for_request(request, only)
                    return result

                f.dispatch = wrapper
                return f
            else:
                @wraps(f)
                def wrapper(request, *args, **kwargs):
                    if before:
                        self.activate_for_request(request, only)

                    result = f(request, *args, **kwargs)

                    if not before:
                        self.activate_for_request(request, only)
                    return result

                return wrapper

        if callable(f):
            return actual_wrap(f)
        else:
            return actual_wrap

    def activate_for_request(self, request, only=False):
        if not hasattr(request, 'active_menus') or only:
            request.active_menus = {self}
        else:
            request.active_menus.add(self)

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def build(self, request):
        if callable(self.visibility) and not self.visibility(request, self):
            return None

        result = {
            'title': self.title,
            'url': self.make_url(request),
            'items': [],
            'active': hasattr(request, 'active_menus') and self in request.active_menus
        }
        result.update(self.kwargs)

        for menu_item in self.items:
            item = menu_item.build(request)
            if item is None:
                continue

            if item['active'] and not result['active']:
                result['active'] = 'subitem'

            result['items'].append(item)

        return result

    def make_url(self, request):
        if self.cached_url is not False:
            return self.cached_url
        elif self.route is None:
            return None
        elif callable(self.route):
            return self.route(request, self)
        elif self.route.startswith('!'):
            return self.route[1:]
        else:
            return reverse(self.route)

    def cache_route(self):
        if not callable(self.route):
            self.cached_url = self.make_url(None)

        for item in self.items:
            item.cache_route()


class MenuMeta(type):
    # noinspection PyProtectedMember,PyUnresolvedReferences
    def __init__(cls, what, bases=None, dict=None):
        super(MenuMeta, cls).__init__(what, bases, dict)
        cls._cls_index = MenuItem._counter
        MenuItem._counter += 1

        cls.prepare()


class Menu(six.with_metaclass(MenuMeta)):
    root_item = None

    # noinspection PyUnresolvedReferences,PyProtectedMember,PyProtectedMember
    @classmethod
    def prepare(cls):
        menu_items = []

        for name, field in cls.__dict__.items():
            if name.startswith('__'):
                continue

            menu_item = None
            if isinstance(field, MenuItem):
                if field.title is None:
                    field.title = name
                menu_item = field
            elif isinstance(field, type) and issubclass(field, Menu):
                field.prepare()
                menu_item = field.root_item

            if menu_item:
                menu_items.append(menu_item)

        kwargs = {}
        if hasattr(cls, 'Meta'):

            for cls_name, cls_field in cls.Meta.__dict__.items():
                if not cls_name.startswith('__'):
                    kwargs[cls_name] = cls_field

        if 'title' not in kwargs:
            kwargs['title'] = cls.__name__

        cls.root_item = root_item = MenuItem(**kwargs)
        root_item._index = cls._cls_index

        menu_items.sort(key=lambda item: item._index)
        root_item.items = menu_items

    @classmethod
    def activate(cls, f=None, only=False):
        return cls.root_item.activate(f, only)

    @classmethod
    def build(cls, request):
        if cls.root_item is None:
            raise ValueError("root_item is None. Did you forget to call prepare()?")
        return cls.root_item.build(request)

    @classmethod
    def cache_routes(cls):
        cls.root_item.cache_route()


def build_menu(request, class_or_name):
    if isinstance(class_or_name, type) and issubclass(class_or_name, Menu):
        return class_or_name.build(request)
    else:
        (module, class_name) = class_or_name.rsplit('.', 1)
        clazz = getattr(import_module(module), class_name)
        return clazz.build(request)
