""" Gerrit client interface.

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

from Queue import Queue, Empty, Full

from pygerrit.error import GerritError
from pygerrit.events import GerritEventFactory
from pygerrit.stream import GerritStream


class GerritClient(object):

    """ Gerrit client interface. """

    def __init__(self, host):
        self._factory = GerritEventFactory()
        self._host = host
        self._events = Queue()
        self._stream = None

    def start_event_stream(self):
        """ Start streaming events from `gerrit stream-events`. """
        if not self._stream:
            self._stream = GerritStream(self, host=self._host)
            self._stream.start()

    def stop_event_stream(self):
        """ Stop streaming events from `gerrit stream-events`."""
        if self._stream:
            self._stream.stop()
            self._stream.join()
            self._stream = None
            with self._events.mutex:
                self._events.queue.clear()

    def get_event(self, block=True, timeout=None):
        """ Get the next event from the queue.

        Return a `GerritEvent` instance, or None if:
         - `block` is False and there is no event available in the queue, or
         - `block` is True and no event is available within the time
        specified by `timeout`.

        """
        try:
            return self._events.get(block, timeout)
        except Empty:
            return None

    def put_event(self, json_data):
        """ Create event from `json_data` and add it to the queue.

        Raise GerritError if the queue is full, or the factory could not
        create the event.

        """
        try:
            event = self._factory.create(json_data)
            self._events.put(event)
        except Full:
            raise GerritError("Unable to add event: queue is full")
