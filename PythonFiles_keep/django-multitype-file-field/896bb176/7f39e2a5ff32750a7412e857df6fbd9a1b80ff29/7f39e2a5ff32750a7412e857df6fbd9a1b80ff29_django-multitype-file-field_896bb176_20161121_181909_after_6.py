# -*- coding: utf-8 -*-
import mimetypes

ARCHIVE_EXTENSIONS = ['.tar', '.tar.bz2', '.tar.gz', '.tgz', '.tz2', '.zip']


def is_archive(mime_type):
    archive_types = ARCHIVE_EXTENSIONS
    for ext in archive_types:
        t_mime, _ = mimetypes.guess_type('t' + ext)
        if t_mime == mime_type:
            return True
    return False
