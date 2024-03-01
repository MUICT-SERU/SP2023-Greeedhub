from contextlib import contextmanager
import io
from io import TextIOBase
import os
import subprocess
import sys

from six import string_types

PY3 = sys.version_info[0] == 3


if PY3:
    def my_popen(cmd, mode='r', buffering=-1):
        """Originated from python os module

        Extend for supporting mode == 'rb' and 'wb'

        Args:
            cmd (str):
            mode (str):
            buffering (int):
        """
        if not isinstance(cmd, str):
            raise TypeError(
                'invalid cmd type (%s, expected string)' % type(cmd))
        if buffering == 0 or buffering is None:
            raise ValueError('popen() does not support unbuffered streams')
        if mode == 'r':
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    bufsize=buffering)
            return _wrap_close(io.TextIOWrapper(proc.stdout), proc)
        elif mode == 'rb':
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    bufsize=buffering)
            return _wrap_close(proc.stdout, proc)
        elif mode == 'w':
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    bufsize=buffering)
            return _wrap_close(io.TextIOWrapper(proc.stdin), proc)
        elif mode == 'wb':
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    bufsize=buffering)
            return _wrap_close(proc.stdin, proc)
        else:
            raise TypeError('Unsupported mode == {}'.format(mode))
else:
    my_popen = os.popen


class _wrap_close(object):
    """Originated from python os module

    A proxy for a file whose close waits for the process
    """
    def __init__(self, stream, proc):
        self._stream = stream
        self._proc = proc

    def close(self):
        self._stream.close()
        returncode = self._proc.wait()
        if returncode == 0:
            return None
        if os.name == 'nt':
            return returncode
        else:
            return returncode << 8  # Shift left to match old behavior

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __iter__(self):
        return iter(self._stream)


@contextmanager
def _stdstream_wrap(fd):
    yield fd


def open_like_kaldi(name, mode='r'):
    """Open a file like kaldi io

    Args:
        name (str or file):
        mode (str):
    """
    # If file descriptor
    if not isinstance(name, string_types):
        if PY3 and 'b' in mode and isinstance(name, TextIOBase):
            return name.buffer
        else:
            return name

    name = name.strip()
    if name[-1] == '|':
        return my_popen(name[:-1], mode)
    elif name[0] == '|':
        return my_popen(name[1:], mode)
    elif name == '-' and 'r' in mode:
        if mode == 'rb' and PY3:
            return _stdstream_wrap(sys.stdin.buffer)
        else:
            return _stdstream_wrap(sys.stdin)
    elif name == '-' and ('w' in mode or 'a' in mode):
        if (mode == 'wb' or mode == 'ab') and PY3:
            return _stdstream_wrap(sys.stdout.buffer)
        else:
            return _stdstream_wrap(sys.stdout)
    else:
        return open(name, mode)


@contextmanager
def open_or_fd(fname, mode):
    # If fname is a file name
    if isinstance(fname, string_types):
        f = open(fname, mode)
    # If fname is a file descriptor
    else:
        if PY3 and 'b' in mode and isinstance(fname, TextIOBase):
            f = fname.buffer
        else:
            f = fname
    yield f

    if isinstance(fname, string_types):
        f.close()


def convert_to_slice(string):
    slices = []
    for ele in string.split(','):
        if ele == '' or ele == ':':
            slices.append(slice(None))
        else:
            args = []
            for _ele in ele.split(':'):
                if _ele == '':
                    args.append(None)
                else:
                    args.append(int(_ele))
            slices.append(slice(*args))
    return tuple(slices)


class MultiFileDescriptor(object):
    """What is this class?

    First of all, I want to load all format kaldi files
    only by using read_kaldi function, and I want to load it
    from file and file descriptor including standard input stream.
    To judge its file format it is required to make the
    file descriptor read and seek(to return original position).
    However, stdin is not seekable, so I create this clas.
    This class joints multiple file descriptors
    and I assume this class is used as follwoing,

        >>> string = fd.read(size)
        >>> # To check format from string
        >>> _fd = StringIO(string)
        >>> newfd = MultiFileDescriptor(_fd, fd)
    """
    def __init__(self, *fds):
        self.fds = fds
        self._current_idx = 0

    def read(self, size):
        if len(self.fds) <= self._current_idx:
            return b''
        string = self.fds[self._current_idx].read(size)
        remain = size - len(string)
        if remain > 0:
            self._current_idx += 1
            string2 = self.read(remain)
            return string + string2
        else:
            return string
