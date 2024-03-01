# -*- coding: utf-8 -*-
import os
import mock
from unittest import TestCase

from multitype_file_field import MultiTypeFileField

from django.conf import settings
from django.core.files.base import ContentFile

from .models import TestModel

UPLOAD_TO = 'multitype'


class GenericTestCase(TestCase):
    def setUp(self):
        with open(os.path.join(settings.FIXTURES_ROOT, 'test.png'), 'rb') as f:
            self.image = ContentFile(f.read(), name=f.name)

        self.common_file = ContentFile('test', name='text.txt')

        self.fake_instance = TestModel()

    def test_empty(self):
        self.assertIsNone(self.fake_instance.file.file_type)

    def test_common_file(self):
        self.fake_instance.file = self.common_file
        self.assertIsNone(self.fake_instance.file.file_type)

    def test_image_file(self):
        self.fake_instance.file = self.image
        self.assertEqual(self.fake_instance.file.file_type, 'image')
