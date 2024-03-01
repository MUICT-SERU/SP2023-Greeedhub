""" Various filesystem utilities.
"""
import os

import unidecode


def ensure_directory_exists(path, expand_user=True, file=False):
    """ Create a directory if it doesn't exists.

        Expanding '~' to the user's home directory on POSIX systems.
    """
    if expand_user:
        path = os.path.expanduser(path)

    if file:
        directory = os.path.dirname(path)
    else:
        directory = path

    if not os.path.exists(directory) and directory:
        try:
            os.makedirs(directory)
        except OSError as e:
            # A parallel process created the directory after the existence check.
            pass

    return(path)


def valid_filename(directory, filename=None, ascii=False):
    """ Return a valid "new" filename in a directory, given a filename/directory=path to test.

        Deal with duplicate filenames.
    """
    def test_filename(filename, count):
        """ Filename to test for existence.
        """
        fn, ext = os.path.splitext(filename)
        return fn + '({})'.format(count) + ext

    return_path = filename is None

    # Directory is a path.
    if filename is None:
        filename = os.path.basename(directory)
        directory = os.path.dirname(directory)

    if ascii:
        filename = unidecode(unicode(filename))
        filename = ' '.join(filename.splitlines()).strip()
        filename = filename.decode('ascii', 'ignore')

    # Allow for directories.
    items = {item: True for item in os.listdir(directory)}
    if filename in items:
        count = 1
        while test_filename(filename, count) in items:
            count += 1
        if return_path:
            return os.path.join(directory, test_filename(filename, count))
        return test_filename(filename, count)
    else:
        if return_path:
            return os.path.join(directory, filename)
        return filename
