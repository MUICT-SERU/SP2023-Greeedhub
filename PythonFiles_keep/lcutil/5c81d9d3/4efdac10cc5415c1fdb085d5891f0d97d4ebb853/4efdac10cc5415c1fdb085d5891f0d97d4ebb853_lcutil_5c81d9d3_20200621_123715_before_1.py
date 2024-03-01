#!/usr/bin/env python3

""" Use pre-defined defaults to open a file.
"""
import optparse
import mimetypes
import os
from pprint import pprint
from shlex import quote
import subprocess
import sys

# pip3 install python-magic
import magic


ROOT = os.path.dirname(os.path.abspath(__file__))

# Map a file extension (lowercase, tuple) to a command.
EXT_COMMAND = {
    ('jpg', 'jpeg', 'png', 'gif'): 'eog {f}',
    ('epub', 'mobi'): 'fbreader {f}',
    ('pdf', 'djvu'): 'evince {f}',
    ('md',): 'vim {f} && md2pdf --output /tmp/tmpmd2pdf.pdf {f} && evince /tmp/tmpmd2pdf.pdf',
    ('py', 'txt'): 'vim {f}',
    ('csv', 'xls', 'xlsx', 'doc', 'docx', 'ods', 'odt'): 'libreoffice {f}',
    ('mp3', 'mp4', 'avi', 'mkv', 'flv'): 'mplayer {f}',
    ('htm', 'html'): 'firefox {f}',
    ('json', 'diff'): 'komodo {f}',
}

NOT_FOUND = 'echo viewer not configured for {f}'


def known_extensions():
    """ Return a list of known extensions.
    """
    extensions = []
    for exts in EXT_COMMAND:
        extensions.extend(exts)

    return(extensions)


def find_command(ext):
    """ Find the command for a given file-extension.
    """
    # Magic guess_extension returned None.
    if not ext:
        ext = ''

    if ext.startswith('.'):
        ext = ext[1:]

    ext = ext.lower()

    command_ = NOT_FOUND
    for exts, command in EXT_COMMAND.items():
        if ext in exts:
            command_ = command
            break

    return command_


def main():
    parser = optparse.OptionParser(usage='%prog [OPTIONS] file')

    parser.add_option('-q',
                      '--quiet',
                      dest='quiet',
                      action='store_true',
                      default=False,
                      help='direct output >/dev/null')

    options, args = parser.parse_args()

    for filepath in args:
        base, ext = os.path.splitext(filepath)
        command = find_command(ext)

        try:
            if command == NOT_FOUND:
                mime = magic.Magic(mime=True)
                ext = mimetypes.guess_extension(mime.from_file(filepath))
                command = find_command(ext)
        except FileNotFoundError:
            print('File not found. {}'.format(filepath))
            continue

        if options.quiet:
            command += '>/dev/null'

        command = command.format(f=quote(filepath))
        try:
            subprocess.check_call(command, shell=True)
        except KeyboardInterrupt:
            print('Terminating...')
            break
        except subprocess.CalledProcessError:
            print('Error with command: {}'.format(command))


if __name__ == '__main__':
    main()
