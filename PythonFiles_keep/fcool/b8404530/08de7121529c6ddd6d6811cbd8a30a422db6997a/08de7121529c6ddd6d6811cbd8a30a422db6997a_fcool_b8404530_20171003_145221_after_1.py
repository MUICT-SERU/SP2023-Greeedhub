# -*- coding: utf-8 -*-
'''fcool: a cool tool for functional programming
Author: William Song

Features:
    Wrap functions, with domains (codomains)
    Operation of functions
    Memorizing easily

CLasses:
    BaseFunction -> Type (or Domain), Function
    BaseFunction: func: function (or number)
    Function: func,
              domain: Type, the definition domain of func
Functions:
    Interval(a:num, b:num) -> Type
    restrict(t:Type) -> decorator(f:function -> Function(f, t))
Constants:
    TURE, FLASE(Type) represent universal set, empty set

Example:

   t = Type(lambda x:x<5 and isinstance(x, int)) * TRUE  # define type(domain) and functions on it
       <=> Type(lambda x, y:x<5 and isinstance(x, int)) <=> Type(lambda x, y:x<5) & Type(int) * TRUE
   t1 = (Type(lambda x:x>=0)) * TRUE
   G = Function(lambda x,y: 2/x, t)
   F = Function(3, t1)

   print((F+F+F)(2,2), (3*F)(2,2), F.sum(F, F)(2,2))
   print(F(1,2))

   print(G.glue(F)(-3,4), glue(G,F)(3,4))

   t = Type(int) & Type(lambda x:x<2)
   print(t(1)) # test

   ID = Function.iden(Type(int))     # identity function on Z(int)
   print(ID.compose(F)(3,4))

   @restrict(Interval(1,2))          # restricting decorator
   def f(x):
       return x

   print(f(1))
   try:
       print(f(3))
   except Exception as ex:
       print(ex)

   @restrict()
   def g(x):
       return x

   print(g(3))
   g= g | Interval(1,2)            # restricting method
   try:
       print(g(3))
   except Exception as ex:
       print(ex)

   print(g.array(g, g)(2))
   f=Function(lambda x:x+1)
   f.memoize()
   print(f(1))'''

import operator
import functools
from types import FunctionType, BuiltinFunctionType, MethodType
import inspect

_FunctionType = (FunctionType, BuiltinFunctionType)


def arity(func):
    '''return the exact arity of functions
    func -> int or (min, max)
    '''
    argspec = inspect.getargspec(func)
    narg = len(argspec.args)
    if argspec.defaults is None:
        ndef = 0
    else:
        ndef = len(argspec.defaults)
    if argspec.varargs is not None or argspec.kewords is not None:
        return (narg - ndef, None)  # (narg - ndef, infinity)
    else:
        if ndef == 0:
            return narg
        return (narg - ndef, narg)

class Arithmetic(object):
    # mixin class
    def __add__(self, other):
        cpy = self.copy()
        cpy += other
        return cpy

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        cpy = self.copy()
        cpy -= other
        return cpy

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        cpy = self.copy()
        cpy *= other
        return cpy

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        cpy = self.copy()
        cpy /= other
        return cpy

    def inv(self):
        return 1 / self

    def __rtruediv__(self, other):
        return self.inv() * other

    def __pow__(self, other):
        cpy = self.copy()
        cpy **= other
        return cpy

    def __mod__(self, other):
        cpy = self.copy()
        cpy %= other
        return cpy

    def __floordiv__(self, other):
        cpy = self.copy()
        cpy //= other
        return cpy

    def __lshift__(self, other):
        cpy = self.copy()
        cpy <<= other
        return cpy

    def __rshift__(self, other):
        cpy = self.copy()
        cpy >>= other
        return cpy

    def __and__(self, other):
        cpy = self.copy()
        cpy &= other
        return cpy

    def __or__(self, other):
        cpy = self.copy()
        cpy |= other
        return cpy

    def __xor__(self, other):
        cpy = self.copy()
        cpy ^= other
        return cpy

    def op(self, other, operator=operator.add):
        cpy = self.copy()
        cpy.iop(other, operator)      # not implemented in this class
        return cpy

    def opn(self, operator, *others):
        cpy = self.copy()
        cpy.iopn(operator, *others)   # not implemented in this class
        return cpy



class BaseFunction(Arithmetic):
    '''function without domain
        func: function or number (regarded as constant function) or set (as characteristic function)'''
    def __init__(self, func):
        if isinstance(func, BaseFunction):   # deprecated
            self.func = func.func
            # print('It is deprecated to set func as a Function object.')
        elif isinstance(func, _FunctionType):
            self.func = func
        elif isinstance(func, set):
            self.func = lambda x: x in func
        # elif isinstance(func, dict):
        #     self.func = lambda x : func[x]
        else:           # func is a number
            self.func = func
        # self.memoize()
        self.__memo = {}
        self.call = self.__originalCall

    def copy(self):
        return BaseFunction(self.func)

    def select(self, call):
        # select calling method
        self.call = MethodType(call, self)

    def update_memo(self, dict_):
        self.__memo.update(dict_)

    def del_memo(self):
        self.__memo = {}

    def memoize(self):
        def call(obj, *args, **kwargs):
            # kwrags is ignored!
            if args in obj.memo:
                return obj.memo[args]
            if isinstance(obj.func, _FunctionType):
                val = obj.func(*args, **kwargs)
            else:            # func is a number
                val = obj.func
            obj.update_memo({args: val})
            return val
        self.select(call)

    def unmemoize(self):
        self.select(self.__originalCall)

    def forget(self):
        self.del_memo()
        self.unmemoize()

    def __originalCall(self, *args, **kwargs):
        if isinstance(self.func, _FunctionType):
            val = self.func(*args, **kwargs)
        else:            # func is a number
            val = self.func
        return val


    def __call__(self, *args, **kwargs):
        # called as a function
        return self.call(*args, **kwargs)
    
    @property
    def arity(self):
        if isinstance(self.func, _FunctionType):
            return arity(self.func)
        return 0

    # general operator:
    def iop(self, other, operator=operator.add):
        # augmented assignment
        cpy = self.copy()       # copy it neccessarily
        if other is self:
            other = cpy
        if isinstance(other, _FunctionType + (BaseFunction,)):
            def f(*args, **kwargs):
                return operator(cpy(*args, **kwargs), other(*args, **kwargs))
        else:
            def f(*args, **kwargs):
                return operator(cpy(*args, **kwargs), other)
        self.func = f
        return self

    def iopn(self, operator, *others):
        # augmented assignment
        cpy = self.copy()       # copy it neccessarily
        def f(*args, **kwargs):
            args = []
            for other in others:
                if isinstance(other, _FunctionType + (BaseFunction,)):
                    if other is self:
                        other = cpy
                    args.append(other(*args, **kwargs))
                else:
                    args.append(other)
            return operator(cpy(*args, **kwargs), *args)
        self.func = f
        return self

    def rop(self, other, operator=operator.add):
        # right operator
        cpy = self.copy()
        if isinstance(other, _FunctionType + (BaseFunction,)):
            def f(*args, **kwargs):
                return operator(other(*args, **kwargs), cpy(*args, **kwargs))
        else:
            def f(*args, **kwargs):
                return operator(other, cpy(*args, **kwargs))
        return self.__class__(f)

    def op1(self, operator=operator.pos):
        # unary operator
        cpy = self.copy()
        def f(*args, **kwargs):
            return operator(cpy(*args, **kwargs))
        return self.__class__(f)

    # operators
    def __iadd__(self, other):
        self.iop(other)
        return self

    def __pos__(self):
        return f.copy()

    def __neg__(self):
        return self.op1(operator=operator.neg)

    def __isub__(self, other):
        self.iop(other, operator=operator.sub)
        return self

    def __imul__(self, other):
        self.iop(other, operator=operator.mul)
        return self

    def __itruediv__(self, other):
        self.iop(other, operator=operator.truediv)
        return self

    def __rtruediv__(self, other):
        return self.rop(other, operator=operator.truediv)

    def __ifloordiv__(self, other):
        self.iop(other, operator=operator.floordiv)
        return self

    def __rfloordiv__(self, other):
        return self.rop(other, operator=operator.floordiv)

    def __ipow__(self, other):
        self.iop(other, operator=operator.pow)
        return self

    def __rpow__(self, other):
        return self.rop(other, operator=operator.pow)

    def __imod__(self, other):
        self.iop(other, operator=operator.mod)
        return self

    def __rmod__(self, other):
        return self.rop(other, operator=operator.mod)

    def __irshift__(self, other):
        self.iop(other, operator=operator.rshift)
        return self

    def __rrshift__(self, other):
        return self.rop(other, operator=operator.rshift)

    def __ilshift__(self, other):
        self.iop(other, operator=operator.lshift)
        return self

    def __rlshift__(self, other):
        return self.rop(other, operator=operator.lshift)

    def __iand__(self, other):
        self.iop(other, operator=operator.and_)
        return self

    def __rand__(self, other):
        return self.rop(other, operator=operator.and_)

    def __ior__(self, other):
        self.iop(other, operator=operator.or_)
        return self

    def __ror__(self, other):
        return self.rop(other, operator=operator.or_)

    def __ixor__(self, other):
        self.iop(other, operator=operator.xor)
        return self

    def __rxor__(self, other):
        return self.rop(other, operator=operator.xor)

    def __abs__(self):
        return self.op1(operator=operator.abs)

    def __invert__(self):
        return self.op1(operator=operator.invert)

    # comparison:
    def __eq__(self, other):
        return self.op(other, operator=operator.eq)

    def __ne__(self, other):
        return self.op(other, operator=operator.ne)

    def __lt__(self, other):
        return self.op(other, operator=operator.lt)

    def __gt__(self, other):
        return self.op(other, operator=operator.gt)

    def __le__(self, other):
        return self.op(other, operator=operator.le)

    def __ge__(self, other):
        return self.op(other, operator=operator.ge)

    def __getitem__(self, index):
        def f(*args, **kwargs):
            return self(*args, **kwargs)[index]
        return self.__class__(f, self.domain)

    def tensor(self, other):
        def f(x, y):
            return self(x) * other(y)
        return self.__class__(f)


class Type(BaseFunction):
    '''implementaion of definition domains of functions
    func: * -> {True, False}'''
    def __init__(self, func=True):
        super(Type, self).__init__(func)
        if isinstance(func, type) or isinstance(func, tuple) and all(isinstance(f, type) for f in func):
            self.func = func

    def __call__(self, *args, **kwargs):
        # called as a function
        func = self.func
        if isinstance(func, type) or isinstance(func, tuple) and all(isinstance(f, type) for f in func):
            return isinstance(args[0], func)
        # elif isinstance(func, type) or isinstance(func, tuple) and all(isinstance(f, type) for f in func):
        #     return all(isinstance(arg, func) for arg in args) and all(isinstance(arg, func) for k, arg in kwargs.items())
        else:            # func is a constant
            return super(Type, self).__call__(*args, **kwargs)

    def __repr__(self):
        if self.func is True or self.func is None:
            return 'Universal set'
        elif self.func is False:
            return 'Empty set'
        elif isinstance(self.func, type):
            return repr(self.func)
        elif isinstance(self.func, tuple) and all(isinstance(f, type) for f in self.func):
            return '|'.join(map(str, self.func))
        else:
            return repr(self.func)

    def copy(self):
        return Type(self.func)

    def isuniversal(self):
        return self.func is True

    def isempty(self):
        return self.func is False

    def __contains__(self, a):
        if isinstance(a, tuple):
            return self(*a)
        return self(a)

    def __imul__(self, other):
        # Cartesian product
        cpy = self.copy()        # neccessarily
        if other is self:
            other = cpy
        if isinstance(other, Type) and other.isempty() or other is False or self.isempty():
            self.func = False
        else:
            def f(x, y):
                return cpy(x) and other(y)
            self.func = f
        return self

    def __ior__(self, other):
        # union
        cpy = self.copy()        # neccessarily
        if other is self:
            other = cpy
        if isinstance(other, Type) and other.func is True or other is True or self.func is True:
            self.func = True
        elif isinstance(other, Type) and other.func is False or other is False:
            pass
        elif self.func is False:
            self.func = other.func if isinstance(other, Type) else other
        else:
            super(Type, self).__ior__(other)
        return self

    def __iand__(self, other):
        # intersection
        cpy = self.copy()        # neccessarily
        if other is self:
            other = cpy
        if isinstance(other, Type) and other.func is False or other is False or self.func is False:
            self.func = False
        elif isinstance(other, Type) and other.func is True or other is True:
            pass
        elif self.func is True:
            self.func = other.func if isinstance(other, Type) else other
        else:
            super(Type, self).__iand__(other)
        return self

    def __ipow__(self, n):
        if n==1:
            return self
        elif n==2:
            self *= self
        elif n % 2 ==0:
            self *= self
            self **= n//2
        else:
            cpy = self.copy()
            self **= n//2
            self *= cpy
        return self

class Domain(Type):
    # alias for Type
    pass


TRUE = Type()        # x is always in TRUE
FALSE = Type(False)  # x is never in FALSE

def Interval(lb=None, ub=None):
    '''lb: [None]lower bound
    ub: [None]upper bound
    where None represents infinity'''
    if lb is None:
        return Type(lambda x: x <= ub)
    elif ub is None:
        return Type(lambda x: lb <= x)
    else:
        return Type(lambda x: lb <= x <= ub)


class Function(BaseFunction):
    '''Function with domain
    func: FunctionType, function/number
    domain: Type[TRUE], definition domain of func
    codomain: Type[None], range (codomain) of func
    name: name of function'''
    def __init__(self, func, domain=None, codomain=None, name=''):
        if isinstance(func, BaseFunction):
            self.func = func.func
            if isinstance(func, Function):
                self.domain = func.domain
                self.codomain = func.codomain
            else:
                self.domain = domain
                self.codomain = codomain
        else:
            super(Function, self).__init__(func)
            self.domain = domain
            self.codomain = codomain
        self.name = name

    def __call__(self, *args, **kwargs):
        # test whether arguments are in the domain (except None), then called as a function
        if self.domain and not self.domain(*args):
            raise Exception('argument is not in definition domain of the function!')
        return super(Function, self).__call__(*args, **kwargs)

    def copy(self):
        if self.domain:
            return Function(self.func, self.domain.copy(), name=self.name)
        else:
            return Function(self.func, None, name=self.name)

    def __repr__(self):
        if self.domain.isuniversal():
            return repr(self.func)
        else:
            return '%s: %s -> '%(repr(self.func), repr(self.domain), repr(self.codomain))


    @staticmethod
    def iden(domain=None):
        # identity function on domain
        return Function(lambda x:x, domain)

    def reduce(self, *others, operator=operator.add):
        return functools.reduce(lambda f,g: f.op(g, operator), (self,) + others)

    def sum(self, *others):
        return self.reduce(*others)

    def prod(self, *others):
        return self.reduce(*others, operator=operator.mul)

    def restrict(self, domain, codomain=None):
        # restricted on domain
        cpy = self.copy()
        if self.domain:
            cpy.domain &= domain
        else:
            cpy.domain = domain
        return cpy

    def __or__(self, other):
        if isinstance(other, Type):        # restriction
            return self.restrict(other)
        return super(Function, self).__or__(other)

    # advanced methods:
    def glue(self, *others, default=None):
        # glue funcitons
        if len(others) == 0:
            def f(*args, **kwargs):
                try:
                    return self(*args, **kwargs)
                except Exception as ex:                     # not in domain of f
                    if default is not None:
                        return default
                    else:
                        raise ex
            return Function(f, self.domain)
        elif len(others) == 1:
            def h(*args, **kwargs):
                try:
                    return self(*args, **kwargs)
                except:
                    try:                                    # not in domain of f
                        return others[0](*args, **kwargs)
                    except Exception as ex:                 # not in domain of f and g
                        if default is not None:
                            return default
                        else:
                            raise ex
            if self.domain:
                if Function(others[0]).domain:
                    return Function(h, self.domain | Function(others[0]).domain)
                else:
                    return Function(h, self.domain)
            else:
                return Function(h, Function(others[0]).domain)
        else:
            return self.glue(others[0], default=default).glue(*others[1:], default=default)

    def compose(self, *others):
        # compose: self(other(x))
        if len(others) == 0:
            return cpy
        elif len(others) == 1:
            def h(*args, **kwargs):
                return self(others[0](*args, **kwargs))
            return Function(h, self.domain)
        else:
            return self.compose(other[0]).compose(*others[1:])

    def o(self, *others):
        return self.compose(*others)

    def rcompose(self, *others):
        # compose: other(self(x))
        cpy = self.copy()
        if len(others) == 0:
            return cpy
        elif len(others) == 1:
            def h(*args, **kwargs):
                return others[0](self(*args, **kwargs))
            return Function(h, self.domain)
        else:
            return self.rcompose(other[-1]).compose(*others[:-1])

    def partial(self, *args):
        return Function(functools.partial(self.func, *args), self.domain)

    def freduce(self, *others, foperator):
        # call fop
        return Function(functools.reduce(lambda f,g: f.fop(g, foperator), (self,) + others), self.domain)

    def fop(self, other, foperator):
        # foperator should act on functions (instead of the values of functions)
        return Function(foperator(self.func, other.func if isinstance(other, Function) else other), self.domain)

    def map(self, *args):
        return map(self.func, *args)

    # others:
    def cat(self, *others):
        def f(*args, **kwargs):
            return self(*args, **kwargs) + [other(*args, **kwargs) for other in others]
        return Function(f, self.domain)

    def inv(self):
        def f(*args, **kwargs):
            return self.func(*args, **kwargs).inv()
        return Function(f, self.domain)

    def array(self, *others):
        def f(x):
            return (self(x),) + tuple(other(x) if isinstance(other, (Function, FunctionType)) else other for other in others)
        return Function(f, self.domain)

    def extend(self):
        if isinstance(self.func, _FunctionType):
            self.func = extend(self.func)


def glue(*fs, default=None):
    # glue(F1,F2, ...) to glue functions F1 F2, ...
    if len(fs) == 1:
        def f(*args, **kwargs):
            try:
                return fs[0](*args, **kwargs)
            except Exception as ex:                     # not in domain of f
                if default is not None:
                    return default
                else:
                    raise Exception('out of domain')
        return Function(f)
    elif len(fs) == 2:
        def f(*args, **kwargs):
            try:
                return fs[0](*args, **kwargs)
            except:
                try:                                    # not in domain of f
                    return fs[1](*args, **kwargs)
                except Exception as ex:                 # not in domain of f and g
                    if default is not None:
                        return default
                    else:
                        raise Exception('out of domain')
        return Function(f)
    else:
        return glue(glue(fs[0], fs[1], default=default), fs[2], default=default)


def restrict(domain=TRUE, codomain=None):
    # this is a decorator, restrict a function on domain
    def F(f):
        return Function(f, domain, codomain)
    return F


def extend(f):
    # decorator, extending function f(x, y) to advanced function f(f1(x),f2(x))
    def g(*Fs):
        def h(x):
            return f(*tuple(F(x) if isinstance(F, _FunctionType) else F for F in Fs))
        return h
    return g


class MathFunction(Function):
    '''Function class only for math
    unable to use keyword arguments
    '''
    def __init__(self, *args, **kwargs):
        super(MathFunction, self).__init__(*args, **kwargs)

    def memoize(self):
        def call(obj, *args):
            if args in obj.memo:
                return obj.memo[args]
            if isinstance(obj.func, _FunctionType):
                val = obj.func(*args)
            else:            # func is a number
                val = obj.func
            obj.update_memo({args: val})
            return val
        self.select(call)

    def forget(self):
        self.del_memo()
        self.call = self.select(self.__originalCall, self)

    def __originalCall(self, *args):
        if isinstance(self.func, _FunctionType):
            val = self.func(*args)
        else:            # func is a number
            val = self.func
        return val


    def __call__(self, *args):
        # called as a function
        return self.call(*args)
        



if __name__ == "__main__":
    # test

    t = (Type(lambda x:x<0)) * TRUE    # define type(domain) and functions on it
    t1 = (Type(lambda x:x>=0)) * TRUE
    G = Function(lambda x,y: 2/x, t)
    F = Function(3, t1)

    # call functions
    print((F+F+F)(2,2), (3*F)(2,2), F.sum(F, F)(2,2))

    print(G.glue(F)(-3,4), glue(G,F)(3,4))

    t = Type(int) & Type(lambda x:x<2)
    print(t(1)) # test

    ID = Function.iden(Type(int))     # identity function on Z(int)
    print(ID.compose(F)(3,4))

    @restrict(Interval(1,2))          # restricting decorator
    def f(x):
        return x

    print(f(1))
    try:
        print(f(3))
    except Exception as ex:
        print(ex)

    @restrict()
    def g(x):
        return x

    print(g(3))
    g= g | Interval(1,2)            # restricting method
    try:
        print(g(3))
    except Exception as ex:
        print(ex)

    print(g.array(g, g)(2))

    f = extend(operator.add)
    print(f(lambda x:x, lambda x:x)(2))
    f = Function(operator.add)
    f.extend()
    print(f(lambda x:x, lambda x:x)(2))

    f=Function(lambda x:x+1)
    f.memoize()
    print(f(1))