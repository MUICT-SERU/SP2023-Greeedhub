from .Base import *
from Mollie.API.Object import Mandate


class Mandates(Base):
    customer_id = None

    def getResourceObject(self, result):
        return Mandate(result)

    def getResourceName(self):
        return 'customers/%s/mandates' % self.customer_id

    def withParentId(self, customer_id):
        self.customer_id = customer_id
        return self

    def on(self, customer):
        return self.withParentId(customer['id'])
