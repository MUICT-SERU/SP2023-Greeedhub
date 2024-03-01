# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import UnsupportedOperation

__author__ = 'luckydonald'

import os
import tarfile

from django.views.generic import View
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.utils.six import b, BytesIO


class BaseTarView(View):
    """A base view to tar and stream several files."""

    http_method_names = ['get']
    tarfile_name = 'download.tar'

    def get_files(self):
        """Must return a list of django's `File` objects."""
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        temp_file = ContentFile(b(""), name=self.tarfile_name)
        with tarfile.TarFile(fileobj=temp_file, mode='w', debug=3) as tar_file:
            files = self.get_files()
            for file_ in files:
                file_name = file_.name
                try:
                    data = file_.read()
                except UnicodeDecodeError:
                    pass
                file_.seek(0, os.SEEK_SET)
                size = len(data)
                try:
                    if isinstance(data, bytes):
                        lol = BytesIO(data)
                    else:
                        lol = BytesIO(data.encode())
                except UnicodeDecodeError:
                    pass
                try:
                    info = tar_file.gettarinfo(fileobj=file_)
                except UnsupportedOperation:
                    info = tarfile.TarInfo(name=file_name)
                info.size = size
                tar_file.addfile(tarinfo=info, fileobj=lol)
        file_size = temp_file.tell()
        temp_file.seek(0)

        response = HttpResponse(temp_file, content_type='application/x-tar')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.tarfile_name
        response['Content-Length'] = file_size
        return response
