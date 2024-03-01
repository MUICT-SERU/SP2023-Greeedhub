
""" Tools to make working with s/FTP servers easier.
"""
import logging
import os
import time

import ftputil
import paramiko


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class FTPUploadFailure(Exception):
    pass


def ensure_directory_exists(sftp, path):
    """ Ensure the path exists on the sFTP server.

        Only if it has the permissions to create the path.
    """
    sep = os.path.sep
    parts = path.split(sep)
    for idx, part in enumerate(parts, 1):
        p = sep.join(parts[:idx])
        if p in ['', '.']:
            continue
        try:
            sftp.mkdir(p)
        except:
            pass


def ensure_upload(ftp, src, dst, attempts=3):
    """ Ensure FTP/sFTP file upload.
    """
    src_size = os.stat(src).st_size

    for attempt in range(attempts):
        if isinstance(ftp, ftputil.host.FTPHost):
            ftp.upload(src, dst)
            dst_size = ftp.stat(dst).st_size
        elif isinstance(ftp, paramiko.sftp_client.SFTPClient):
            ftp.put(src, dst)
            dst_size = ftp.stat(dst).st_size
        if src_size == dst_size:
            break

        time.sleep(3)
    else:
        raise FTPUploadFailure('Tries exceeded.')

    return(attempt)
