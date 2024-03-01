from oscar.apps.shipping import repository
from kgx.ecommerce.oscar.methods import KGXRegularShipping


class Repository(repository.Repository):
    """ Example repository for KGX.  Likely you're going to want to implement your own version.
    """
    def __init__(self):
        self.__methods = []

    def get_default_shipping_method(self, basket, shipping_addr=None, **kwargs):
        methods = list(filter(
            lambda m: m.code == 'code',
            self.get_available_shipping_methods(basket, shipping_addr, **kwargs))
        )
        if methods:
            return methods[0]

    def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
        if not self.__methods:
            self.__methods = [KGXRegularShipping(shipping_addr), ]
        return self.__methods
