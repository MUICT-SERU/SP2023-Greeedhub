from enum import Enum


class PickupType(Enum):
    """ Indicates one of 3 types of pickup allowed for scheduling by KGX.
    Although these 3 exist, they may not be available for all locations or all customers.
    """
    next_day_service = 'NDS'
    same_day_service = 'SDS'
    regular = 'regular'

    @classmethod
    def _missing_(cls, value):
        # BS to gracefully handle API inconsistencies
        # different endpoints return different names for these values
        try:
            return {
                'nds': cls.next_day_service,
                'sds': cls.same_day_service,
                'reg': cls.regular,
                'reguler': cls.regular,
            }[value]
        except KeyError:
            return super()._missing_(value)