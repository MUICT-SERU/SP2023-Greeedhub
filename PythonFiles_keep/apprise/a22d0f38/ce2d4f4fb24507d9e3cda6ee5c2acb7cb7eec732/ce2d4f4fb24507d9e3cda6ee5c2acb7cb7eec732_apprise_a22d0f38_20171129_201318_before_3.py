# -*- coding: utf-8 -*-
#
# base class for easier library inclusion
#
# Copyright (C) 2017 Chris Caron <lead2gold@gmail.com>
#
# This file is part of apprise.
#
# apprise is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# apprise is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with apprise. If not, see <http://www.gnu.org/licenses/>.

from .common import NotifyType
from .common import NOTIFY_TYPES
from .common import NOTIFY_IMAGE_SIZES
from .common import NotifyImageSize
from .plugins.NotifyBase import NotifyFormat

from .Apprise import Apprise
from .AppriseAsset import AppriseAsset

__version__ = '0.0.1'
__author__ = 'Chris Caron <lead2gold@gmail.com>'

__all__ = [
    # Core
    'Apprise', 'AppriseAsset',

    # Reference
    'NotifyType', 'NotifyImageSize', 'NotifyFormat', 'NOTIFY_TYPES',
    'NOTIFY_IMAGE_SIZES',
]
