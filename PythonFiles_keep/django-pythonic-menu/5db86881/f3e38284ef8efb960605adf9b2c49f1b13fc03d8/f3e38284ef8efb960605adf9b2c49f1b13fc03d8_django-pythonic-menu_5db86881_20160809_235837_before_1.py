from importlib import import_module

from django.template.library import Library

from django_pythonic_menu.menu import Menu

register = Library()


@register.simple_tag(takes_context=True)
def render_menu(context, menu_class):
    request = context['request']
    if issubclass(menu_class, Menu):
        return menu_class.build(request)
    else:
        (module, class_name) = menu_class.rsplit('.', 1)
        clazz = getattr(import_module(module), class_name)
        return clazz.build(request)
