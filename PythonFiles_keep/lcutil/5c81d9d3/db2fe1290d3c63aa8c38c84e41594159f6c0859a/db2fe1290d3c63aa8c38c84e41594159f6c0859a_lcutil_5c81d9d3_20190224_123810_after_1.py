#!/usr/bin/env python

""" Find all files modified between two dates, default 1 day apart.
"""
from __future__ import print_function
import datetime
import optparse
import os
import sys


FORMAT = '%Y%m%d'


if __name__ == '__main__':

    parser = optparse.OptionParser()

    parser.add_option('-r',
                      '--root',
                      dest='root',
                      action='store',
                      type='string',
                      default='.',
                      help='root directory to walk')

    parser.add_option('-b',
                      '--start',
                      dest='start',
                      action='store',
                      type='string',
                      default='',
                      help='start date [YYYYMMDD]')

    parser.add_option('-e',
                      '--stop',
                      dest='stop',
                      action='store',
                      type='string',
                      default='',
                      help='stop date [YYYYMMDD]')

    options, args = parser.parse_args()

    if not options.start:
        parser.print_help()
        sys.exit()

    try:
        start = datetime.datetime.strptime(options.start, FORMAT)
    except:
        parser.print_help()
        sys.exit()

    if options.stop in ['']:
        stop = start + datetime.timedelta(days=1)
    else:
        try:
            stop = datetime.datetime.strptime(options.stop, FORMAT)
        except:
            parser.print_help()
            sys.exit()

    for root, dirs, files in sorted(os.walk(options.root)):
        for filename in sorted(files):
            path = os.path.join(root, filename)
            if not os.path.islink(path):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))

                if start < mtime < stop:
                    print(mtime.strftime('%Y%m%dT%H%M%S'), path)
