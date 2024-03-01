import logging
import os
import re
from datetime import datetime

from pytz import timezone


class Workspace(object):
    """Workspace manager class."""

    root = "./results"
    time_zone = timezone("Asia/Tokyo")
    datetime_fmt = "%Y%m%d_%H%M%S"

    def __init__(self,
                 name="experiment",
                 root="./results"):
        self.category, self.name = re.match(r"(?:(.+)/)?(.+)", name).groups("")
        Workspace.root = root
        self.created = datetime.now(Workspace.time_zone)
        self.path = os.path.join(Workspace.root,
                                 self.category,
                                 "{}_{}".format(self.created.strftime(Workspace.datetime_fmt), self.name))
        self.logger = None

    def log(self, message):
        """Logging"""
        if self.logger is None:
            self._init_logger()

        self.logger.info(message)

    def _init_logger(self):
        logging.basicConfig(filename=self._get_abs_path("result.log"),
                            format="[%(asctime)s %(name)s] %(message)s",
                            datefmt="%Y/%m/%d %I:%M:%S",
                            level=logging.DEBUG)
        self.logger = logging.getLogger(self.name)

    def _get_abs_path(self, relpath=""):
        """Convert relative path to absolute path based on workspace directory."""
        abspath = os.path.abspath(os.path.join(self.path, relpath))
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        return abspath

    def __call__(self, relpath=""):
        return self._get_abs_path(relpath)
