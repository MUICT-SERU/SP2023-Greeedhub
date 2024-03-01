from sysscribe import cpuinfo

def dev_list():
    cpuinfo = cpuinfo()
    cpu_list=[]
    for processor in cpuinfo.keys():
        cpu_list.append(cpuinfo[processor]['model name'])
    return cpu_list
        
def print_list():
    cpuinfo = cpuinfo()
    for processor in cpuinfo.keys():
        print(cpuinfo[processor]['model name'])
        
