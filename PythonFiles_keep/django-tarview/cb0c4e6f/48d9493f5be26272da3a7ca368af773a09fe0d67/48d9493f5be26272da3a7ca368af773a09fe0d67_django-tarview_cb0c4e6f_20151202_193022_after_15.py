# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.core.files.base import ContentFile

import os
import tarfile

from django.test import TestCase
from django.core.files import File
from django.http import HttpResponse
from django.test.client import RequestFactory

from tarview.views import BaseTarView


class TarView(BaseTarView):
    """Test TarView basic implementation."""
    _files = None

    def get_files(self):
        if self._files is None:
            dirname = os.path.dirname(__file__)
            self._files = [
                File(open(os.path.join(dirname, 'test_file.txt')), name="test_file.txt"),
                File(open(os.path.join(dirname, 'test_file.odt')), name="test_file.odt"),
                ContentFile(b"Littlepip is best pony!", name="test_file_manual.txt")
            ]
        return self._files


class TarViewTests(TestCase):
    def setUp(self):
        self.view = TarView()
        self.request = RequestFactory()

    def test_response_type(self):
        response = self.view.get(self.request)
        self.assertTrue(isinstance(response, HttpResponse))

    def test_response_params(self):
        response = self.view.get(self.request)
        self.assertEqual(response['Content-Type'], 'application/x-tar')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=download.tar')

    def test_response_content_length(self):
        response = self.view.get(self.request)
        self.assertEqual(response['Content-Length'], '10240')  # measured manually with Finder.

    def test_valid_tarfile(self):
        response = self.view.get(self.request)
        with open("/tmp/test.tar", mode="wb") as file:
            file.write(response.content)
        response_file = ContentFile(response.content, name="test.tar")
        self.assertTrue(tarfile.is_tarfile("/tmp/test.tar"))
        tar_file = tarfile.TarFile(fileobj=response_file)
        self.assertEqual(tar_file.getnames(), ['test_file.txt', 'test_file.odt', 'test_file_manual.txt'])

    def tearDown(self):
        import os
        if os.path.exists("/tmp/test.tar"):
            os.unlink("/tmp/test.tar")
        pass
