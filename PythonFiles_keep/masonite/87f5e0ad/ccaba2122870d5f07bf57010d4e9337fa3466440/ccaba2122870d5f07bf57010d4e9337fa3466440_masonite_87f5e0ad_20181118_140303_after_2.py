""" Upload Disk Driver """

import os

from masonite.contracts import UploadContract
from masonite.drivers import BaseUploadDriver
from masonite.app import App


class UploadDiskDriver(BaseUploadDriver, UploadContract):
    """Upload to and from the file system.
    """

    file_location = None

    def __init__(self, app: App):
        """Upload Disk Driver Constructor

        Arguments:
            StorageConfig {config.storage} -- Storage configuration.
            Application {masonite.app.App} -- The application container.
        """

        self.config = app.make('StorageConfig')
        self.appconfig = app.make('Application')

    def store(self, fileitem, filename=None, location=None):
        """Store the file onto a server.

        Arguments:
            fileitem {cgi.Storage} -- Storage object.

        Keyword Arguments:
            location {string} -- The location on disk you would like to store the file. (default: {None})
            filename {string} -- A new file name you would like to name the file. (default: {None})

        Returns:
            string -- Returns the file name just saved.
        """

        if filename is None:
            filename = os.path.basename(fileitem.filename)

        # Check if is a valid extension
        self.validate_extension(filename)

        location = self.get_location(location)
        if not location.endswith('/'):
            location += '/'

        open(location + filename, 'wb').write(fileitem.file.read())

        self.file_location = location + filename

        return filename
