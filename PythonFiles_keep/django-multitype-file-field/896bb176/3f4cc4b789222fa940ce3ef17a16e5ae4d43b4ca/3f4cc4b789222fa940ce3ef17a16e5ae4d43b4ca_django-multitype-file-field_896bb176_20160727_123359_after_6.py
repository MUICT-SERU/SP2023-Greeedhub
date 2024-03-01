# -*- coding: utf-8 -*-
import mimetypes

from django.forms import ClearableFileInput
from easy_thumbnails.widgets import ImageClearableFileInput


class MultiTypeFileInput(ImageClearableFileInput):
    def render(self, name, value, attrs=None):
        if value:
            mime, encoding = mimetypes.guess_type(value.name)
            p_type, s_type = mime.split('/')
            if p_type != 'image':
                self.template_with_initial = ClearableFileInput.template_with_initial
                return ClearableFileInput.render(self, name, value, attrs)
        return super(MultiTypeFileInput, self).render(name, value, attrs)