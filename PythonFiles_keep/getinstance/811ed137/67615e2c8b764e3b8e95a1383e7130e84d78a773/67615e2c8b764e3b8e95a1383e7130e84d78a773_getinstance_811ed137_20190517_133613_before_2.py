from getinstance import InstanceManager

class Country:
    instances = InstanceManager()
    
    def __init__(self, name):
        self.name = name
            
au = Country('Australia')
ru = Country('Russia')

print(Country.instances.all())
print(Country.instances.get(name='Australia')) 
