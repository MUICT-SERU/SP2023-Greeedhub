
from sysscribe import meminfo

def total_memory():
    meminfo = meminfo()
    print('Total memory: {0}'.format(meminfo['MemTotal']))
