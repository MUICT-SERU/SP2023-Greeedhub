# We use the Map resolver to override an argument's default value 
# that is better suited for our needs.

from argresolver import Map

# Let's assume we cannot touch this code...
class Foo:
    def __init__(self, arg1, arg2='I_dont_like_this_default'):
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return "Foo(arg1='{self.arg1}', arg2='{self.arg2}')".format(self=self)

# But we can alter the class and wrap a resolver around the class __init__ 
Foo.__init__ = Map(dict(arg2="better_default"), default_override=True)(Foo.__init__)

foo = Foo("this is arg1")
print(str(foo))  # Foo(arg1='this is arg1', arg2='better_default')