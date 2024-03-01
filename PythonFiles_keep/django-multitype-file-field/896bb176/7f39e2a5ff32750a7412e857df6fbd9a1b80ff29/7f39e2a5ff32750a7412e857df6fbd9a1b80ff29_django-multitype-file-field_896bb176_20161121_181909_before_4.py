# -*- coding: utf-8 -*-
import ImageFile
import mimetypes

from django.db import models
from django.db.models.fields.files import FieldFile

from multitype_file_field.forms import MultiTypeFormField


class MultiTypeFileField(models.FileField):
    attr_classes = {
        None: FieldFile,
        'image': ImageFile,
    }

    def get_attr_reverse_map(self):
        return {cls: key for key, cls in self.attr_classes.items()}

    @staticmethod
    def is_archive(mime_type):
        archive_types = ['.tar', '.tar.bz2', '.tar.gz', '.tgz', '.tz2', '.zip']
        for ext in archive_types:
            t_mime, _ = mimetypes.guess_type('t' + ext)
            if t_mime == mime_type:
                return True
        return False

    def get_attr_keys(self, instance, field, file_name):
        keys = []
        if file_name is None:
            return keys

        mime, encoding = mimetypes.guess_type(file_name)
        if mime:
            p_type, s_type = mime.split('/')
            if self.is_archive(mime):
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