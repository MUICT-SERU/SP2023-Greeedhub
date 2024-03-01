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

    def activate(self, f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'active_menus'):
                request.active_menus = {self}
            else:
                request.active_menus.add(self)
            return f(request, *args, **kwargs)

        return wrapper

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
        if self.route is None:
            return None
        elif callable(self.route):
            return self.route(request, self)
        elif self.route.startswith('!'):
            return self.route[1:]
        else:
            return reverse(self.route)


class MenuMeta(type):
    # noinspection PyProtectedMember,PyUnresolvedReferences
    def __init__(cls, what, bases=None, dict=None):
        super(MenuMeta, self).__init__(what, bases, dict)
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
    def activate(cls, f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'active_menus'):
                request.active_menus = {cls.root_item}
            else:
                request.active_menus.add(cls.root_item)
            return f(request, *args, **kwargs)

        return wrapper

    @classmethod
    def build(cls, request):
        if cls.root_item is None:
            raise ValueError("root_item is None. Did you forget to call prepare()?")
        return cls.root_item.build(request)
