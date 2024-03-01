# -*- coding: utf-8 -*-
import inspect
import mimetypes

from django.forms.widgets import ClearableFileInput
from django.contrib.admin.widgets import AdminFileWidget


try:
    from easy_thumbnails.widgets import ImageClearableFileInput

    AdminImageWidget = ImageClearableFileInput
except ImportError:
    ImageClearableFileInput = ClearableFileInput
    AdminImageWidget = AdminFileWidget



class MultiTypeInputMixin(object):
    widget_classes = {
        'image': ImageClearableFileInput
    }

    def __init__(self, widgets=None, *args, **kwargs):
        self._widgets = widgets or self.widget_classes
        for k, w in self._widgets.items():
            if inspect.isclass(w):
                self._widgets[k] = w(*args, **kwargs)
        super(MultiTypeInputMixin, self).__init__(*args, **kwargs)

    def _get_widget(self, name, value, attrs):
        file_type = getattr(value, 'file_type', None)
        if file_type:
            return self._widgets.get(file_type)
        return None

    def render(self, name, value, attrs=None):
        widget = self._get_widget(name, value, attrs)
        if widget:
            return widget.render(name, value, attrs)
        return super(MultiTypeInputMixin, self).render(name, value, attrs=None)


class MultiTypeClearableFileInput(MultiTypeInputMixin, ClearableFileInput):
    pass


class AdminMultiTypeClearableFileInput(MultiTypeInputMixin, AdminFileWidget):
    widget_classes = {
        'image': AdminImageWidget
    }

