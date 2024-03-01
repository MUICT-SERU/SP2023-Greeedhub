import json
from enum import Enum

from behave import given, when, then
from behave.runner import Context

from kgx import KGXClient
from kgx.responses import RateEstimate, AbstractDeserializableResponse, DeliveryScheduledResponse


class SimulationType(Enum):
    request = 'request'
    response = 'response'


SIMULATED_JSON = {
    '/check_rate': {
        SimulationType.response: {
            "origin_zipcode": "10110",
            "destination_zipcode": "13350",
            "weight": 8,
            "services": {
                "sds": {
                    "FinalCost": 200000,
                    "CODFee": 0,
                    "DeliveryFee": 200000,
                    "VAT": 0,
                    "InsuranceFee": 0
                },
                "nds": {
                    "FinalCost": 120000,
                    "CODFee": 0,
                    "DeliveryFee": 120000,
                    "VAT": 0,
                    "InsuranceFee": 0
                },
                "reguler": {
                    "FinalCost": 72000,
                    "CODFee": 0,
                    "DeliveryFee": 72000,
                    "VAT": 0,
                    "InsuranceFee": 0
                }
            }
        },
        SimulationType.request: {
            "origin_zipcode": "10110",
            "destination_zipcode": "13350",
            "weight": 8,
            "product_price": 0,
            "is_insurance": False,
            "is_cod": False
        }
    },
    '/create_order': {
        SimulationType.request: {
            "web_order_id": "12345678",
            "sender": {
                "name": "Angela",
                "mobile": "+62 87654321",
                "email": "angela@example.com"
            },
            "origin": {
                "address": "Jl. Kebagusan 1",
                "city": "Jakarta Barat",
                "state": "Jakarta Barat",
                "country": "Indonesia",
                "postcode": "11410"
            },
            "origin_comments": "Use the side door",
            "recipient": {
                "name": "Sven",
                "mobile": "+62 12345678",
                "email": "sven@example.com"
            },
            "destination": {
                "address": "Jl. Kebagusan 10",
                "city": "Jakarta Barat",
                "state": "Jakarta Barat",
                "country": "Indonesia",
                "postcode": "11410"
            },
            "package": {
                "quantity": 1,
                "transaction_value": 100000,
                "item_full_price": 120000,
                "insurance": False,
                "photo": "http://www.flickr.com/bird.jpg",
                "size": "Motorcycle",
                "weight": 1,
                "volume": 0.1,
                "note": "Fragile",
                "width": 1,
                "height": 1,
                "length": 1,
                "locker_dropoff": False
            },
            "merchant_id": "MRCHNT-123",
            "paid_by_parent": False,
            "is_cod": False,
            "pickup_time": 1475402400,
            "pickup_type": "NDS",
            "destination_comments": "Call 123 if nobody is in."
        },
        SimulationType.response: {
            "status": "OK",
            "order_number": "EDS12345678",
            "web_order_id": "12345678",
            "label_url": "http://api.staging.etobee.com/api/print_label?order_number=EDS67455165",
            "message": "Booking in progress"
        },
    }
}


@given('a simulated response from {endpoint}')
def step_impl(context: Context, endpoint: str) -> None:
    try:
        context.simulated_json = SIMULATED_JSON[endpoint][SimulationType.response]
    except KeyError:
        raise RuntimeError(f'Misconfigured test: No simulated responses for "{endpoint}"')


@given('a production API client')
def step_impl(context: Context) -> None:
    context.client = KGXClient(
        credentials=('my_username', 'my_password'),
        sandbox_mode=False
    )


@when('I deserialize the response as {class_name}')
def step_impl(context: Context, class_name: str) -> None:
    try:
        cls: AbstractDeserializableResponse = {
            'RateEstimate': RateEstimate,
            'DeliveryScheduledResponse': DeliveryScheduledResponse,
        }[class_name]
        context.response = cls.from_api_json(context.simulated_json)
    except KeyError:
        raise RuntimeError(f'Misconfigured test: Unknown class "{class_name}"')

KEYNOTFOUND = '<KEYNOTFOUND>'       # KeyNotFound for dictDiff
def dict_diff(first, second):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one fo the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dicationary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    diff = {}
    # Check all keys in first dict
    for key in first.keys():
        if not key in second:
            diff[key] = (first[key], KEYNOTFOUND)
        elif (first[key] != second[key]):
            diff[key] = (first[key], second[key])
    # Check all keys in second dict to find missing
    for key in second.keys():
        if not key in first:
            diff[key] = (KEYNOTFOUND, second[key])
    return diff

@then("the request is serialized correctly for {endpoint}")
def step_impl(context: Context, endpoint: str) -> None:
    expected_json = SIMULATED_JSON[endpoint][SimulationType.request]
    actual_json = json.loads(context.serialized_request)

    diff = dict_diff(expected_json, actual_json)


    assert expected_json == actual_json


@then('the request is a {method} made to {url}')
def step_impl(context: Context, method: str, url: str) -> None:
    call = context.requests_mock.post.call_args
    assert call[0][0] == url


@then('the request credentials are set properly')
def step_impl(context: Context):
    call = context.requests_mock.post.call_args
    auth = call[1]['auth']
    assert ('my_username', 'my_password') == auth


@then('the response is properly deserialized')
def step_impl(context: Context):
    response = context.response
