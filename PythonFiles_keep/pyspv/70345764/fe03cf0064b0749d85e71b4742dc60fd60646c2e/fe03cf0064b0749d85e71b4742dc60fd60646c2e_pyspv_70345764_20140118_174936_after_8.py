
DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

def bytes_to_hexstring(data, reverse=True):
    if reverse:
        return ''.join(reversed(['{:02x}'.format(v) for v in data]))
    else:
        return ''.join(['{:02x}'.format(v) for v in data])

def hexstring_to_bytes(s, reverse=True):
    if reverse:
        return bytes(reversed([int(s[x:x+2], 16) for x in range(0, len(s), 2)]))
    else:
        return bytes([int(s[x:x+2], 16) for x in range(0, len(s), 2)])

