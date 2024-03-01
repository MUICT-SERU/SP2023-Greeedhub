from sysscribe import pciinfo

def pci_list():
    pciinfo = pciinfo()
    pci_list=[]
    for pci in pci_list.keys():
        pci_list.append(pciinfo[pci])
    return pci_list
        
def print_list():
    pciinfo = pciinfo()
    for pci in pci_list.keys():
        print(pciinfo[pci])
        
