from unittest.mock import MagicMock

from behave import given, then, when
from requests import Response

from kgx import KGXClient
from kgx.common import PickupType
from kgx.requests import CheckRateRequest
from kgx.responses import RateEstimateDetail


@then("the response is deserialized correctly for a RateEstimate")
def step_impl(context):
    assert context.response.origin_zipcode == '10110'
    assert context.response.destination_zipcode == '13350'
    assert context.response.weight == 8
    assert context.response.services == {
        PickupType.same_day_service:
            RateEstimateDetail(final_cost=200000, cod_fee=0, delivery_fee=200000, vat=0, insurance_fee=0),
        PickupType.next_day_service:
            RateEstimateDetail(final_cost=120000, cod_fee=0, delivery_fee=120000, vat=0, insurance_fee=0),
        PickupType.regular:
            RateEstimateDetail(final_cost=72000, cod_fee=0, delivery_fee=72000, vat=0, insurance_fee=0)
    }


@given('a simulated CheckRateRequest request')
def step_impl(context):
    context.simulated_request = CheckRateRequest(
        origin_zipcode='10110',
        destination_zipcode='13350',
        weight=8,
        product_price=0,
        is_insurance=False,
        is_cod=False
    )


@when('I serialize the request')
def step_impl(context):
    c = KGXClient(('a', 'a'), False)
    context.serialized_request = c._serialize_request(
        context.simulated_request)


@when('I perform a rate lookup')
def step_impl(context):
    client: KGXClient = context.client

    mock = MagicMock(spec=Response)
    mock.json = lambda: context.simulated_json

    context.requests_mock.post.return_value = mock

    context.response = client.check_rate(
        CheckRateRequest(
            origin_zipcode='10110',
            destination_zipcode='13350',
            weight=8,
            product_price=0,
            is_insurance=False,
            is_cod=False
        )
    )

