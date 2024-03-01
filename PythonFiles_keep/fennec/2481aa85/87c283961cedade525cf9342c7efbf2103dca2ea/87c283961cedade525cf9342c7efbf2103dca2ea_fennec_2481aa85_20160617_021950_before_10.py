import os
from datetime import datetime

from pytz import timezone


class Workspace(object):
    """Workspace manager class."""

    root_path = "./results"
    time_zone = timezone("Asia/Tokyo")
    datetime_fmt = "%Y%m%d%H%M%S"

    def __init__(self, name=None, time=None):
        self.name = name if name else "experiment"
        self.created = time if time else datetime.now(Workspace.time_zone)
        self.dir_path = os.path.join(Workspace.root_path,
                                     "{}-{}".format(self.created.strftime(Workspace.datetime_fmt), self.name))
        self.logger = None

    def get_abs_path(self, relpath):
        """Convert relative path to absolute path based on workspace directory."""
        abspath = os.path.abspath(os.path.join(self.dir_path, relpath))
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        return abspath

    @classmethod
    def set_root_path(cls, path):
        cls.root_path = path

    @classmethod
    def set_time_zone(cls, timezone_str):
        cls.time_zone = timezone(timezone_str)

    @classmethod
    def set_datetime_format(cls, datetime_fmt):
        cls.datetime_fmt = datetime_fmt

    def __call__(self, relpath):
        return self.get_abs_path(relpath)
