################################################################################
#                                                                              #
#   utils.py                                                                   #
#                                                                              #
#   General utility module.                                                    #
#                                                                              #
#                                                                              #
#                                                                              #
#   Copyright (C) 2015 LibreLabUCM All Rights Reserved.                        #
#                                                                              #
#   This file is part of teleg-api-bot.                                        #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                              #
################################################################################

#!/usr/bin/python

from inspect import getmembers
import pprint
pp = pprint.PrettyPrinter(indent=4)


def msgGetSummary(msg, truncate = 0):
    if not msg["text"] == None:
        return (msg["text"][:truncate] + '...') if (len(msg["text"]) > truncate and truncate is not 0) else msg["text"]
    if not msg["media"] == None:
        return "Media: " + str(msg["media"]["type"])
    if not msg["new_chat_participant"] == None:
        return msg["new_chat_participant"]["print_name"] + " was added to " + msg["chat"]["title"]
    else:
        return ":O"
