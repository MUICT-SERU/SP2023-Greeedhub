# -*- coding: utf-8 -*-
import mimetypes

from django import forms
from easy_thumbnails.widgets import ImageClearableFileInput


class MultiTypeFormField(forms.ImageField):
    _widget = forms.ImageField.widget

    def _get_widget(self, value=None):
        if value:
            mime, encoding = mimetypes.guess_type(value)
            if mime:
                p_type, s_type = mime.split('/')
                if p_type == 'image':
                    return ImageClearableFileInput()
        return self._widget

    widget = property(_get_widget)

    def _set_widget(self, widget):
        self._widget = widget

    widget = widget.setter(_set_widget)

    def to_python(self, data):
        if data:
            mime, encoding = mimetypes.guess_type(data.name)
            if mime:
                p_type, s_type = mime.split('/')
                if p_type == 'image':
                    return super(MultiTypeFormField, self).to_python(data)
        return forms.FileField.to_python(self, data)