# -*- coding: utf-8 -*-
import inspect
import mimetypes
from django.contrib.admin import options
from django.db import models

from .utils import is_archive
from .widgets import MultiTypeClearableFileInput, AdminMultiTypeClearableFileInput


class MultiTypeFileField(models.FileField):
    field_classes = {
        'image': models.ImageField,
    }

    def __init__(self, verbose_name=None, fields=None, get_field=None, *args, **kwargs):

        super(MultiTypeFileField, self).__init__(verbose_name, *args, **kwargs)

        self.field_map = fields
        if not self.field_map:
            self.field_map = {key: field_class(*args, **kwargs) for key, field_class in
                              self.field_classes.items()}
        else:
            for k, field in self.field_map.items():
                field_kwargs = dict(kwargs)
                if isinstance(field, tuple):
                    field, extra_kwargs = field
                    field_kwargs.update(extra_kwargs)

                if inspect.isclass(field):
                    self.field_map[k] = field(*args, **field_kwargs)

        self.field_map.setdefault(None, models.FileField(*args, **kwargs))

        if get_field:
            self._get_field = get_field

    def get_attr_reverse_map(self):
        return {cls: key for key, cls in self.attr_classes.items()}

    def _get_field_keys(self, instance, field, file_name):
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

    def _copy_attrs(self, from_field, to_field):
        attrs = [
            'auto_created',
            'validators',
            'editable',
            'serialize',
            'error_messages',
            'help_text',
            'name',
            'verbose_name']
        for a in attrs:
            setattr(to_field, a, getattr(from_field, a))
        return to_field

    def _get_field(self, instance, field, file_name):
        attr_class = (None, self.field_map[None])
        for _t_type in self._get_field_keys(instance, field, file_name):
            try:
                attr_class = (_t_type, self.field_map[_t_type])
                break
            except KeyError:
                pass
        return attr_class

    def _attr_class_wrap(self):

        def _wrap(instance, field, file_name):
            attr_name, new_field = self._get_field(instance, field, file_name)
            new_field = self._copy_attrs(field, to_field=new_field)
            _attr = field.attr_class(instance, new_field, file_name)
            _attr.file_type = attr_name
            return _attr

        return _wrap

    attr_class = property(_attr_class_wrap)

    def formfield(self, **kwargs):
        kwargs.setdefault('widget', MultiTypeClearableFileInput)
        return super(MultiTypeFileField, self).formfield(**kwargs)


options.FORMFIELD_FOR_DBFIELD_DEFAULTS[MultiTypeFileField] = {
    'widget': AdminMultiTypeClearableFileInput
}
