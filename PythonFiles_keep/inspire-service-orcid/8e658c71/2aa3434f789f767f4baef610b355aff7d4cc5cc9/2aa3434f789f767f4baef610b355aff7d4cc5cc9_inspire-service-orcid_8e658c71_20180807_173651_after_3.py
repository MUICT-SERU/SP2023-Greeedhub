import re

from six.moves import range

SPLIT_KEY_PATTERN = re.compile('\.|\[')


def get_value(record, key, default=None):
    """
    Note: copied from inspire_utils
    https://github.com/inspirehep/inspire-utils/blob/master/inspire_utils/record.py
    This is the only code used from that package. If more code will be uased,
    the right strategy would be to use the inspire_utils library directly.

    Return item as `dict.__getitem__` but using 'smart queries'.

    .. note::

        Accessing one value in a normal way, meaning d['a'], is almost as
        fast as accessing a regular dictionary. But using the special
        name convention is a bit slower than using the regular access:
        .. code-block:: python
            >>> %timeit x = dd['a[0].b']
            100000 loops, best of 3: 3.94 us per loop
            >>> %timeit x = dd['a'][0]['b']
            1000000 loops, best of 3: 598 ns per loop
    """
    def getitem(k, v, default):
        if isinstance(v, dict):
            return v[k]
        elif ']' in k:
            k = k[:-1].replace('n', '-1')
            # Work around for list indexes and slices
            try:
                return v[int(k)]
            except IndexError:
                return default
            except ValueError:
                return v[slice(*map(
                    lambda x: int(x.strip()) if x.strip() else None,
                    k.split(':')
                ))]
        else:
            tmp = []
            for inner_v in v:
                try:
                    tmp.append(getitem(k, inner_v, default))
                except KeyError:
                    continue
            return tmp

    # Check if we are using python regular keys
    try:
        return record[key]
    except KeyError:
        pass

    keys = SPLIT_KEY_PATTERN.split(key)
    value = record
    for k in keys:
        try:
            value = getitem(k, value, default)
        except KeyError:
            return default
    return value


def chunked_sequence(sequence, chunk_size):
    """
    Yield successive chunk_size sized chunks from sequence.
    """
    if not chunk_size > 0:
        raise ValueError('chunk_size must be > 0')
    for i in range(0, len(sequence), chunk_size):
        yield sequence[i:i + chunk_size]
