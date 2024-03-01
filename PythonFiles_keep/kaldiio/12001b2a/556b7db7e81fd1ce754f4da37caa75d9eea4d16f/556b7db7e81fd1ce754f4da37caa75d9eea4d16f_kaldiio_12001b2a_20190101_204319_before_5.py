from functools import partial
from io import BytesIO
import sys
import wave

import numpy as np
from scipy.io import wavfile as wavfile

from kaldiio.utils import convert_to_slice
from kaldiio.utils import LazyLoader
from kaldiio.utils import open_like_kaldi
from kaldiio.utils import open_or_fd


PY3 = sys.version_info[0] == 3

if PY3:
    from collections.abc import Mapping
else:
    from collections import Mapping


def load_wav_scp(fname,
                 segments=None,
                 separator=None, dtype='int', return_rate=True):
    if segments is None:
        return _load_wav_scp(fname, separator=separator, dtype=dtype,
                             return_rate=return_rate)
    else:
        return SegmentsExtractor(fname, separator=separator, dtype=dtype,
                                 return_rate=return_rate, segments=segments)


def _load_wav_scp(fname, separator=None, dtype='int', return_rate=True):
    assert dtype in ['int', 'float'], 'int or float'
    loader = LazyLoader(partial(load_wav,
                                dtype=dtype,
                                return_rate=return_rate))
    with open_or_fd(fname, 'r') as fd:
        for line in fd:
            token, wavname = line.split(separator, 1)
            loader[token] = wavname.strip()
    return loader


class SegmentsExtractor(Mapping):
    """Emulate the following,

    https://github.com/kaldi-asr/kaldi/blob/master/src/featbin/extract-segments.cc

    Args:
        segments (str): The file format is
            "<segment-id> <recording-id> <start-time> <end-time>\n"
            "e.g. call-861225-A-0050-0065 call-861225-A 5.0 6.5\n"
    """
    def __init__(self, fname,
                 segments=None, separator=' ', dtype='int', return_rate=True):
        self.wav_scp = fname
        self.wav_loader = _load_wav_scp(self.wav_scp, separator=separator,
                                        dtype=dtype, return_rate=return_rate)

        self.segments = segments
        self._segments_dict = {}
        with open(self.segments) as f:
            for l in f:
                sps = l.strip().split(' ')
                if len(sps) != 4:
                    raise RuntimeError('Format is invalid: {}'.format(l))
                uttid, recodeid, st, et = sps
                self._segments_dict[uttid] = (recodeid, float(st), float(et))

                if recodeid not in self.wav_loader:
                    raise RuntimeError(
                        'Not found "{}" in {}'.format(recodeid, self.wav_scp))

    def __iter__(self):
        return iter(self._segments_dict)

    def __contains__(self, item):
        return item in self._segments_dict

    def __len__(self):
        return len(self._segments_dict)

    def __getitem__(self, key):
        recodeid, st, et = self._segments_dict[key]
        rate, array = self.wav_loader[recodeid]
        # Convert starting time of the segment to corresponding sample number.
        # If end time is -1 then use the whole file starting from start time.
        if et != -1:
            return rate, array[int(st * rate):int(et * rate)]
        else:
            return rate, array[int(st * rate):]


def load_wav(wav_name, return_rate=True, dtype='int'):
    assert dtype in ['int', 'float'], 'int or float'
    slices = None
    if ':' in wav_name:
        fname, offset = wav_name.split(':', 1)
        if '[' in offset and ']' in offset:
            offset, Range = offset.split('[')
            slices = convert_to_slice(Range.replace(']', '').strip())
        offset = int(offset)
    else:
        fname = wav_name
        offset = None

    try:
        with open_like_kaldi(fname, 'rb') as fd:
            rate, array = read_wav(fd, offset, dtype=dtype)
    # If wave error found, try scipy.wavfile
    except wave.Error:
        with open_like_kaldi(fname, 'rb') as fd:
            rate, array = read_wav2(fd, offset, dtype=dtype)

    if slices is not None:
        array = array[slices]
    if return_rate:
        return rate, array
    else:
        return array


def read_wav(fd, offset=None, dtype='int', return_size=False):
    if offset is not None:
        fd.seek(offset)
    wd = wave.open(fd)
    assert isinstance(wd, wave.Wave_read)
    rate = wd.getframerate()
    nchannels = wd.getnchannels()
    nbytes = wd.getsampwidth()
    if nbytes == 2:
        dtype = dtype + '16'
    elif nbytes == 4:
        dtype = dtype + '32'
    elif nbytes == 8:
        dtype = dtype + '64'
    else:
        raise ValueError('bytes_per_sample must be 2, 4 or 8')
    data = wd.readframes(wd.getnframes())
    size = 44 + len(data)
    array = np.frombuffer(data, dtype=np.dtype(dtype))
    if nchannels > 1:
        array = array.reshape(-1, nchannels)

    if return_size:
        return (rate, array), size
    else:
        return rate, array


def read_wav2(fd, offset=None, dtype='int', return_size=False):
    if offset is not None:
        fd.seek(offset)
    # scipy.io.wavfile doesn't support streaming input
    data = fd.read()
    size = len(data)
    fd2 = BytesIO(data)
    rate, array = wavfile.read(fd2)

    if return_size:
        return (rate, array), size
    else:
        return rate, array
