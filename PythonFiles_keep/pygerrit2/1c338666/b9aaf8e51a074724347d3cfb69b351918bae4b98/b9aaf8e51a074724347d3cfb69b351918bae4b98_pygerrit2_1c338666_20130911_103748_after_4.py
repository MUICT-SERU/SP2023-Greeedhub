# The MIT License
#
# Copyright 2012 Sony Mobile Communications. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

"""

import logging
from select import select
from threading import Thread, Event

from .error import GerritError
from .events import ErrorEvent


class GerritStream(Thread):

    """ Gerrit events stream handler. """

    def __init__(self, gerrit, ssh_client):
        Thread.__init__(self)
        self.daemon = True
        self._gerrit = gerrit
        self._ssh_client = ssh_client
        self._stop = Event()

    def stop(self):
        """ Stop the thread. """
        self._stop.set()

    def _error_event(self, error):
        """ Dispatch `error` to the Gerrit client. """
        self._gerrit.put_event(ErrorEvent.error_json(str(error)))

    def run(self):
        """ Listen to the stream and send events to the client. """
        try:
            result = self._ssh_client.run_gerrit_command("stream-events")
        except GerritError as err:
            self._error_event(err)
        else:
            stdout = result.stdout
            inputready, _outputready, _exceptready = \
                select([stdout.channel], [], [])
            while not self._stop.is_set():
                for _event in inputready:
                    try:
                        self._gerrit.put_event(stdout.readline())
                    except IOError as err:
                        self._error_event(err)
                    except GerritError as err:
                        logging.error("Failed to put event: %s", err)
