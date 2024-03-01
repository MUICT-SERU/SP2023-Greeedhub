from importlib import import_module

import six
from django.template.library import Library

from django_pythonic_menu.menu import Menu

register = Library()


@register.simple_tag(takes_context=True)
def render_menu(context, menu_class):
    request = context['request']
    if isinstance(menu_class, six.string_types):
        (module, class_name) = menu_class.rsplit('.', 1)
        clazz = getattr(import_module(module), class_name)
        return clazz.build(request)
    elif issubclass(menu_class, Menu):
        return menu_class.build(request)
