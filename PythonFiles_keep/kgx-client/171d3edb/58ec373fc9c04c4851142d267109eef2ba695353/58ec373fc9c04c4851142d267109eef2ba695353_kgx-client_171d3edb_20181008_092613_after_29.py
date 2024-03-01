from abc import ABCMeta, abstractmethod
from collections import namedtuple
from datetime import datetime
from enum import Enum
from typing import Dict

from .common import PickupType


class AbstractDeserializableResponse(metaclass=ABCMeta):
    """ Essentially the base class for all API responses.  This just defines __slots__
    and ensures that all derived classes need to define a from_api_json class method.
    """
    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_api_json(cls, api_json: dict):
        pass


RateEstimateDetail = namedtuple('RateEstimateDetail', [
    'final_cost',
    'cod_fee',
    'delivery_fee',
    'vat',
    'insurance_fee',
])


class RateEstimate(AbstractDeserializableResponse):

    __slots__ = ['origin_zipcode', 'destination_zipcode', 'weight', 'services', ]

    def __init__(self,
                 origin_zipcode: str,
                 destination_zipcode: str,
                 weight: int,
                 services: Dict[PickupType, RateEstimateDetail]):
        self.origin_zipcode = origin_zipcode
        self.destination_zipcode = destination_zipcode
        self.weight = weight
        self.services = services

    @classmethod
    def from_api_json(cls, api_json: dict):
        return cls(
            origin_zipcode=api_json['origin_zipcode'],
            destination_zipcode=api_json['destination_zipcode'],
            weight=api_json['weight'],
            services={
                PickupType(k): RateEstimateDetail(
                    final_cost=v['FinalCost'],
                    cod_fee=v['CODFee'],
                    delivery_fee=v['DeliveryFee'],
                    vat=v['VAT'],
                    insurance_fee=v['InsuranceFee']
                )
                for k, v in api_json.get('services', {}).items()
            }
        )


class DeliveryScheduledResponse(AbstractDeserializableResponse):
    """ Response returned form the API when a shipment is delivery is scheduled.
    """
    __slots__ = ('status', 'order_number', 'web_order_id', 'label_url', 'message', )

    def __init__(self, status: str, order_number: str, web_order_id: str, label_url: str, message: str):
        self.status = status
        self.order_number = order_number
        self.web_order_id = web_order_id
        self.label_url = label_url
        self.message = message

    @classmethod
    def from_api_json(cls, api_json: dict):
        return cls(**api_json)


class FailedDeliveryAttempt(AbstractDeserializableResponse):
    """ Sub-entity that records an attempt by KGX to deliver
    """
    __slots__ = ('proof_of_attempt', 'attempt_time', 'reason', )

    class DeliveryFailureReason(Enum):
        bad_address = 'BAD_ADDRESS'
        consignee_not_around = 'CONSIGNEE_NOT_AROUND'
        consignee_refused_to_accept = 'CONSIGNEE_REFUSED_TO_ACCEPT'
        consignee_cannot_be_contacted = 'CONSIGNEE_CANNOT_BE_CONTACTED'
        consignee_want_reschedule = 'CONSIGNEE_WANT_RESCHEDULE'
        consignee_does_not_have_enough_cash = 'CONSIGNEE_DOES_NOT_HAVE_ENOUGH_CASH'
        stuff_or_box_is_broken = 'STUFF_OR_BOX_IS_BROKEN'
        stuff_does_not_match_specification = 'STUFF_DOES_NOT_MATCH_SPECIFICATION'
        driver_arrived_too_late = 'DRIVER_ARRIVED_TOO_LATE'
        cod_mismatch = 'COD_MISMATCH'
        out_of_coverage = 'OUT_OF_COVERAGE'
        natural_disaster = 'NATURAL_DISASTER'
        manual_process = 'MANUAL_PROCESS'

    def __init__(self, proof_of_attempt: str, attempt_time: datetime, reason: DeliveryFailureReason):
        self.proof_of_attempt = proof_of_attempt
        self.attempt_time = attempt_time
        self.reason = reason

    @classmethod
    def from_api_json(cls, api_json: dict):
        return cls(**api_json)


class AbstractStatusResponse(AbstractDeserializableResponse, metaclass=ABCMeta):

    __slots__ = ('status', 'order_status', 'web_order_id', 'book_time', )

    class OrderStatus(Enum):
        booked = 'BOOKED'
        not_assigned = 'NOT_ASSIGNED'
        accepted = 'ACCEPTED'
        pickup = 'PICKUP'
        in_transit = 'IN-TRANSIT'
        delivered = 'DELIVERED'
        returned_sender = 'RETURNED_SENDER'
        cancelled = 'CANCELLED'
        missing = 'MISSING'
        claimed_merchant = 'CLAIMED_MERCHANT'
        claimed_vendor = 'CLAIMED_VENDOR'
        claimed_all = 'CLAIMED_ALL'

    def __init__(self, status: str, order_status: OrderStatus, web_order_id: str, book_time: datetime=None):
        self.status = status
        self.order_status = order_status
        self.web_order_id = web_order_id
        self.book_time = book_time

    @classmethod
    def from_api_json(cls, api_json: dict):
        return cls(**api_json)


class NewPickupStatus(AbstractStatusResponse): pass  # CREATED, NOT_ASSIGNED, ACCEPTED, PICKUP
class InTransitStatus(AbstractStatusResponse): pass  # ,	IN-TRANSIT	IN-TRANSIT w/ FAILED
class CancelledOrderStatus(AbstractStatusResponse): pass  # DELIVERED
class ReturnedOrderStatus(AbstractStatusResponse): pass  # CANCELLED
class DeliveredOrderStatus(AbstractStatusResponse): pass  # RETURNED_SENDER


class CancellationResponse(AbstractDeserializableResponse):
    """ Response when a delivery has been successfully cancelled.
    """
    __slots__ = ('status', 'message', )

    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message

    @classmethod
    def from_api_json(cls, api_json: dict):
        return cls(**api_json)
