from math import ceil

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar.apps.address.models import UserAddress
from oscar.apps.basket.abstract_models import AbstractBasket, AbstractLine
from oscar.apps.catalogue.models import ProductClass
from oscar.apps.shipping.methods import Base
from django.db.models import ObjectDoesNotExist
from kgx import KGXClient
from kgx.requests import CheckRateRequest


class KGXRegularShipping(Base):
    """ Shipping method for KGX standard shipping.
    """
    code = 'kgx_regular'
    name = _('KGX Regular')

    def __init__(self, address: UserAddress=None):
        self.client = KGXClient(
            credentials=settings.KGX['CREDENTIALS'],
            sandbox_mode=settings.KGX.get('SANDBOX_MODE', False)
        )
        self.ship_to_address = address
        self.weight_attr_code = settings.KGX['WEIGHT_ATTR_CODE']
        self.default_weight = settings.KGX.get('DEFAULT_WEIGHT_KGS', 1)

    def calculate(self, basket: AbstractBasket):
        total_weight = 0.0
        for line in basket.all_lines():
            if line.is_shipping_required():
                try:
                    weight = line.product.attribute_value.get(
                        attribute__code=self.weight_attr_code
                    ).value_float
                except ObjectDoesNotExist:
                    weight = self.default_weight
                total_weight += weight

        self.client.check_rate(
            CheckRateRequest(
                origin_zipcode='',
                destination_zipcode=self.ship_to_address.postcode,
                weight=int(ceil(total_weight)),
                product_price=1234,
            )
        )
