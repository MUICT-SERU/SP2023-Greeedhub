# We do some automatic dependency injection with fallback

from argresolver import Chain, Const, Map

inject = Chain(
    Map(dict(service1="Service1", service2="Service2")), 
    Const("Fallback Service")
)

class Orchestration:
    @inject
    def business_process1(self, service1, service2):
        print("Calling service:", service1)
        print("Calling service:", service2)

    @inject
    def business_process2(self, service1, service3):
        print("Calling service:", service1)
        print("Calling service:", service3)

orchester = Orchestration()
orchester.business_process1()
# Prints:
# Calling service: Service1
# Calling service: Service2

orchester.business_process2()
# Prints:
# Calling service: Service1
# Calling service: Fallback Service