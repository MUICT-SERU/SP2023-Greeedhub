
from collections import OrderedDict
import platform

from sysscribe import cpu
from sysscribe import memory
from sysscribe import network
from sysscribe import disk

def system_dict():
    
    sysinfo=OrderedDict()

    sysinfo['platform'] = platform.uname()

    # Add cpu info dict
    cpu_list = cpu.dev_list()
    sysinfo['cpu'] = OrderedDict()
    sysinfo['cpu']['num sockets'] = len(cpu_list)
    sysinfo['cpu']['socket type'] = cpu_list[0]
    
    # Add memory info
    sysinfo['memory'] = OrderedDict()
    sysinfo['memory']['total'] = memory.total()
    
    # Add network info
    net_list = network.dev_list()
    sysinfo['network'] = OrderedDict()
    sysinfo['network']['num devices'] = len(net_list)
    sysinfo['network']['devices'] = net_list
    
    # Storage info
    disk_sizes = disk.disk_sizes()
    sysinfo['disk'] = OrderedDict()
    sysinfo['disk']['num devices'] = len(disk_sizes)
    sysinfo['disk']['device size'] = disk_sizes
    
    return sysinfo
    
    