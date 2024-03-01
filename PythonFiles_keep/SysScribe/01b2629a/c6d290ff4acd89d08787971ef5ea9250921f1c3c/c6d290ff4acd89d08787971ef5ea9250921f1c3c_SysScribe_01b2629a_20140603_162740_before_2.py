from sysscribe import cpuinfo

def list_cpu():
    cpuinfo = cpuinfo()
    for processor in cpuinfo.keys():
        print(cpuinfo[processor]['model name'])
        