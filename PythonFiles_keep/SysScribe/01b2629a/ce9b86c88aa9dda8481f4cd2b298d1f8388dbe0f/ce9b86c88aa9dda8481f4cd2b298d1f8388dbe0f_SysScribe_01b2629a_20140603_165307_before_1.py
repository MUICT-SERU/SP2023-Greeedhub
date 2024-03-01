from sysscribe import pciinfo

def pci_list():
    pciinf = pciinfo()
    pci_list=[]
    for pci in pci_list.keys():
        pci_list.append(pciinf[pci])
    return pci_list
        
def print_list():
    pciinf = pciinfo()
    for pci in pci_list.keys():
        print(pciinf[pci])
        
