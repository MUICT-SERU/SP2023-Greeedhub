# -*- coding: utf-8 -*-
import mimetypes

from django.db import models
from django.core.files.images import ImageFile
from django.db.models.fields.files import FieldFile

from .forms import MultiTypeFormField
from .utils import is_archive


class MultiTypeFileField(models.FileField):
    attr_classes = {
        None: FieldFile,
        'image': ImageFile,
    }

    def __init__(self, attr_classes=None, get_attr_class=None, *args, **kwargs):
        if attr_classes:
            self.attr_classes = attr_classes
        if get_attr_class:
            self.get_attr_class = get_attr_class

        super(MultiTypeFileField, self).__init__(*args, **kwargs)

    def get_attr_reverse_map(self):
        return {cls: key for key, cls in self.attr_classes.items()}

    def get_attr_keys(self, instance, field, file_name):
        keys = []
        if file_name is None:
            return keys

        mime, encoding = mimetypes.guess_type(file_name)
        if mime:
            p_type, s_type = mime.split('/')
            if is_archive(mime):
                p_type = 'archive'

            keys = [mime, p_type]
        return keys

    def get_attr_class(self, instance, field, file_name):
        attr_class = (None, self.attr_classes[None])
        for _t_type in self.get_attr_keys(instance, field, file_name):
            try:
                attr_class = (_t_type, self.attr_classes[_t_type])
                break
            except KeyError:
                pass
        return attr_class

    def _attr_class_wrap(self):

        def _wrap(instance, field, file_name):
            attr_name, attr_class = self.get_attr_class(instance, field, file_name)
            _attr = attr_class(instance, field, file_name)
            _attr.attr_name = attr_name
            return _attr

        return _wrap

    attr_class = property(_attr_class_wrap)

    def formfield(self, **kwargs):
        defaults = {'form_class': MultiTypeFormField, 'max_length': self.max_length}
        # If a file has been provided previously, then the form doesn't require
        # that a new file is provided this time.
        # The code to mark the form field as not required is used by
        # form_for_instance, but can probably be removed once form_for_instance
        # is gone. ModelForm uses a different method to check for an existing file.
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(MultiTypeFileField, self).formfield(**defaults)
