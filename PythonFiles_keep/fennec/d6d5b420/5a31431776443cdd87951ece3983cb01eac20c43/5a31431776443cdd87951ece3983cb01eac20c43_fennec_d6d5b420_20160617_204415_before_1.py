from __future__ import print_function

import logging
import os
import re
from datetime import datetime

from pytz import timezone


class Workspace(object):
    """Workspace manager.

    Args:
        name (str): Workspace name. (it is used for directory naming)
        root (str): Root of results.

    Attributes:
        name (str): Workspace name.
        category (str): Workspace category.
    """

    root = "./results"
    zone = timezone("Asia/Tokyo")
    date_fmt = "%Y%m%d_%H%M%S"

    def __init__(self,
                 name="experiment",
                 root="./results"):
        self.category, self.name = re.match(r"(?:(.+)/)?(.+)", name).groups("")
        Workspace.root = root
        self._created = datetime.now(Workspace.zone)
        self._path = os.path.join(Workspace.root,
                                  self.category,
                                  "{}_{}".format(self._created.strftime(Workspace.date_fmt), self.name))
        self._logger = None

    def log(self, message, display=True):
        """Logging"""
        if self._logger is None:
            self._init_logger()

        self._logger.info(message)

        if display:
            print(message)

    def _init_logger(self):
        logging.basicConfig(filename=self._get_abs_path("result.log"),
                            format="[%(asctime)s %(name)s] %(message)s",
                            datefmt="%Y/%m/%d %I:%M:%S",
                            level=logging.DEBUG)
        self._logger = logging.getLogger(self.name)

    def _get_abs_path(self, relpath=""):
        """Convert relative path to absolute path based on workspace directory."""
        abspath = os.path.abspath(os.path.join(self._path, relpath))

        # exist_ok does not exists for os.makedirs in python 2
        if not os.path.exists(abspath):
            os.makedirs(os.path.dirname(abspath))
        return abspath

    def __call__(self, relpath=""):
        return self._get_abs_path(relpath)
