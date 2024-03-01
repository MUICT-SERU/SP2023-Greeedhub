from django.db import models

from multitype_file_field.fields import MultiTypeFileField


class TestModel(models.Model):
    file = MultiTypeFileField(upload_to='test_archive')

