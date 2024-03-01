# -*- coding: utf-8 -*-
from os import path

from luckydonaldUtils.logger import logging

from pytgbot.api_types import TgBotApiObject

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


class Sendable(TgBotApiObject):
    def __init__(self):
        super(Sendable, self).__init__()
    # end def __init__
# end class


class InputFile(object):
    def __init__(self, file_path, file_name=None, file_mime=None):
        super(InputFile, self).__init__()
        self.file_path = file_path
        self.file_name = file_name if file_name else path.basename(file_path)
        self.file_mime = file_mime if file_mime else None

    def get_request_files(self, var_name):
        return {var_name: (self.file_name, open(self.file_path, 'rb'), self.file_mime)}