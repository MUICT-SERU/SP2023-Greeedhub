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


def start_recv():
    '''Open a server on Unix Domain Socket'''
    if os.path.exists(SOCKFILE):
        os.unlink(SOCKFILE)
    unsock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    unsock.bind(SOCKFILE)
    print("Unix socket start listening...")
    i = 0
    while True:
        i += 1
        data = unsock.recv(BUFSIZE)
        parsed_msg = alert.AlertPkt.parser(data)
        if parsed_msg:
            yield parsed_msg
            print('[X] Snort Alert: ' + parsed_msg)

if __name__ == '__main__':
    start_recv()
