from http import HTTPStatus

from behave import given, when, then

from kgx.exceptions import APIErrorResponse, APIExceptionType


@given("API error JSON")
def step_impl(context):
    context.example_json = {
        "error": {
            "message": "The API encountered a fatal error",
            "kind": "FatalException",
            "code": 500
        }
    }


@when("I deserialize it")
def step_impl(context):
    context.example_error = APIErrorResponse.from_api_json(context.example_json)


@then("the error class is instantiated correctly")
def step_impl(context):
    assert context.example_error.message == 'The API encountered a fatal error'
    assert context.example_error.kind == APIExceptionType.fatal_exception
    assert context.example_error.code == HTTPStatus.INTERNAL_SERVER_ERROR
