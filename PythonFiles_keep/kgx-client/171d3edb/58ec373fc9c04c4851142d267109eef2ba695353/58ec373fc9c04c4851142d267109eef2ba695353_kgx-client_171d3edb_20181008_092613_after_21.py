import json
from collections import namedtuple
from datetime import datetime
from enum import Enum
from typing import Tuple, Union, TypeVar, Type

import requests

from .responses import RateEstimate, DeliveryScheduledResponse, CancellationResponse
from .requests import CheckRateRequest, ScheduleDeliveryRequest, CancelDeliveryRequest
from .exceptions import APIErrorResponse, APINotContactable, APIResponseNotJson


__all__ = ['KGXClient', ]


T = TypeVar('T')


class KGXClient:
    """ Facilitates communicating with the KGX API.
    """
    def __init__(self, credentials: Tuple[str, str], sandbox_mode=False):
        self.credentials = credentials
        self.sandbox_mode = sandbox_mode

    @property
    def verify_ssl(self):
        return not self.sandbox_mode

    @property
    def base_url(self):
        return 'https://test-api.kgx.co.id/api' if self.sandbox_mode else 'http://api.kgx.co.id/api'

    def check_rate(self, req: CheckRateRequest) -> RateEstimate:
        """ To estimate price of each available service per customer request.
        """
        return self._http_post_json('/check_rate', req, RateEstimate)

    def schedule_delivery(self, req: ScheduleDeliveryRequest) -> DeliveryScheduledResponse:
        """ Schedules a delivery (really, a pickup.
        Calling it a delivery to be consistent with KGX docs) with KGX.
        """
        return self._http_post_json('/create_order', req, DeliveryScheduledResponse)

    def cancel_delivery(self, req: CancelDeliveryRequest) -> CancellationResponse:
        """ Attempts to cancel a delivery which has been scheduled.
        """
        return self._http_post_json('/cancel_order', req, CancellationResponse)

    def _marshal_request(self, payload) -> dict:
        marshalled = {}
        # 1. Skip all non-public attributes (starts with sunder or dunder)
        # 2. special case to ignore 'index' and 'count' attributes for namedtuples
        for attr_name in [a for a in dir(payload)
                          if not a.startswith('_') and a not in ('index', 'count')]:
            attr_val = getattr(payload, attr_name)
            if isinstance(attr_val, datetime):
                marshalled[attr_name] = int(attr_val.timestamp())
            elif isinstance(attr_val, tuple):
                marshalled[attr_name] = self._marshal_request(attr_val)
            elif isinstance(attr_val, Enum):
                marshalled[attr_name] = attr_val.value
            elif isinstance(attr_val, (int, str, bool, float)):
                marshalled[attr_name] = attr_val
            else:
                marshalled[attr_name] = self._marshal_request(attr_val)
        return marshalled

    def _serialize_request(self, payload) -> str:
        return json.dumps(self._marshal_request(payload))

    def _http_post_json(self, url_path: str, payload: Union[dict, namedtuple], response_class: Type[T]) -> T:
        """ Posts some JSON to the KGX API and returns the response.
        """
        try:
            http_response = requests.post(
                f'{self.base_url}{url_path}',
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                data=self._serialize_request(payload),
                auth=self.credentials,
                verify=self.verify_ssl
            )
            if 'error' in http_response.json():
                raise APIErrorResponse.from_api_json(http_response.json())
            return response_class.from_api_json(http_response.json())
        except requests.RequestException as e:
            raise APINotContactable(inner_exception=e)
        except ValueError as e:
            raise APIResponseNotJson(inner_exception=e)
