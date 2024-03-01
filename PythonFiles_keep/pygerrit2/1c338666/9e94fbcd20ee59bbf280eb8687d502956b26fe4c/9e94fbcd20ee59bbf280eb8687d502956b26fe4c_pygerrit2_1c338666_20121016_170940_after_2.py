""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

The MIT License

Copyright 2012 Sony Mobile Communications. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import json
from select import poll, POLLIN
from threading import Thread, Event

from pygerrit.error import GerritError
from pygerrit.events import GerritEvent, GerritEventFactory


@GerritEventFactory.register("gerrit-stream-error")
class GerritStreamErrorEvent(GerritEvent):

    """ Represents an error when handling the gerrit event stream. """

    def __init__(self, json_data):
        super(GerritStreamErrorEvent, self).__init__()
        self.error = json_data["error"]


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

    def run(self):
        """ Listen to the stream and send events to the client. """
        try:
            _stdin, stdout, _stderr = \
                self._ssh_client.run_gerrit_command("stream-events")
            p = poll()
            p.register(stdout.channel)
            while not self._stop.is_set():
                data = p.poll()
                for (fd, event) in data:
                    if fd == stdout.channel.fileno():
                        if event == POLLIN:
                            line = stdout.readline()
                            json_data = json.loads(line)
                            self._gerrit.put_event(json_data)
        except GerritError, e:
            error = json.loads('{"type":"gerrit-stream-error",'
                               '"error":"%s"}' % str(e))
            self._gerrit.put_event(error)
