from collections import namedtuple
from datetime import datetime
from enum import IntEnum

from .common import PickupType


class CancelDeliveryRequest:
    """ Cancels a delivery.

    .. note::

        Cancellation can only be made for deliveries that have status (BOOKED, ACCEPTED, PICKUP).
    """
    __slots__ = ('order_number', 'reason_id', )

    class Reason(IntEnum):
        sender_not_around = 1
        consignee_not_around = 2
        wrong_pickup_address = 3
        wrong_dropoff_address = 4
        vehicle_issue = 5
        technical_issue = 6
        accident = 7
        drivers_location_is_too_far = 8
        fee_is_too_expensive = 9
        i_dont_need_to_delivery_my_item = 10
        i_inserted_the_wrong_address = 11
        i_testing_the_app = 12
        no_driver_available = 13
        i_checking_the_price = 14
        my_wallet_insufficient = 15
        i_wanted_for_too_long = 16
        driver_asked_to_cancel = 17
        cancelled_by_admin = 18
        other = 99

    def __init__(self, order_number: str, reason_id: Reason):
        self.order_number = order_number
        self.reason_id = reason_id


CheckRateRequest = namedtuple('CheckRateRequest', [
    'origin_zipcode',
    'destination_zipcode',
    'weight',
    'product_price',
    'is_insurance',
    'is_cod',
])


Address = namedtuple('Address', [
    'address',
    'city',
    'state',
    'country',
    'postcode',
])


Person = namedtuple('Person', [
    'name',
    'mobile',
    'email',
])


Package = namedtuple('Package', [
    'quantity',
    'transaction_value',
    'item_full_price',
    'insurance',
    'photo',
    'size',
    'weight',
    'volume',
    'note',
    'width',
    'height',
    'length',
    'locker_dropoff'
])


class ScheduleDeliveryRequest:
    __slots__ = (
        'web_order_id', 'sender', 'recipient', 'origin', 'destination', 'package', 'merchant_id', 'is_cod',
        'paid_by_parent', 'pickup_time', 'pickup_type', 'origin_comments', 'destination_comments', )

    def __init__(self,
                 web_order_id: str,
                 sender: Person,
                 origin: Address,
                 recipient: Address,
                 destination: Address,
                 package: Package,
                 merchant_id: str,
                 is_cod: bool=False,
                 paid_by_parent: bool=False,
                 pickup_time: datetime=None,
                 pickup_type: PickupType=None,
                 origin_comments: str=None,
                 destination_comments: str=None):
        self.web_order_id = web_order_id
        self.sender = sender
        self.recipient = recipient
        self.origin = origin
        self.destination = destination
        self.package = package
        self.merchant_id = merchant_id
        self.is_cod = is_cod
        self.paid_by_parent = paid_by_parent
        self.pickup_time = pickup_time
        self.pickup_type = pickup_type
        self.origin_comments = origin_comments
        self.destination_comments = destination_comments

