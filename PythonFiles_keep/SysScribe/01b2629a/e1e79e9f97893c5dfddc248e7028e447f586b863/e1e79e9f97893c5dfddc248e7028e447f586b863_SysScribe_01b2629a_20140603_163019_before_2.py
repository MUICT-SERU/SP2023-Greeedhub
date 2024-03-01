
from sysscribe import meminfo

def total():
    meminfo = meminfo()
    return meminfo['MemTotal']

def print_total():
    print('Total memory: {0}'.format(total()))
