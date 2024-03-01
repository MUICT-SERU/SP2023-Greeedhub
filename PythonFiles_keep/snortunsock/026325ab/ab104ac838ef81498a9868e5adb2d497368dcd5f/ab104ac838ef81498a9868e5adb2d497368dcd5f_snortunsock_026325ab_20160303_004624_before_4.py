# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import socket

import alert

BUFSIZE = alert.AlertPkt._ALERTPKT_SIZE
SOCKFILE = "/tmp/snort_alert"


class SnortListener:

    def __init__(self):
        self.unsock = None

    def start_recv(self):
        self._start_recv()

    def _recv_loop(self):
        '''Receive Snort alert on Unix Domain Socket'''
        print("Unix socket start listening...")
        while True:
            data = self.unsock.recv(BUFSIZE)
            msg = alert.AlertPkt.parser(data)
            if msg:
                print('[X] Snort Alert: ' + msg)

    def _start_recv(self):
        '''Open a server on Unix Domain Socket'''
        if os.path.exists(SOCKFILE):
            os.unlink(SOCKFILE)
        self.unsock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.unsock.bind(SOCKFILE)
        self._recv_loop()

if __name__ == '__main__':
    server = SnortListener()
    server.start_recv()
