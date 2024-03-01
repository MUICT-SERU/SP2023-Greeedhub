"""Fake IZIR API module usable for testing importation of modules"""
import izi


class FakeException(BaseException):
    pass


@izi.directive(apply_globally=False)
def my_directive(default=None, **kwargs):
    """for testing"""
    return default


@izi.default_input_format('application/made-up')
def made_up_formatter(data):
    """for testing"""
    return data


@izi.default_output_format()
def output_formatter(data):
    """for testing"""
    return izi.output_format.json(data)


@izi.get()
def made_up_api(izi_my_directive=True):
    """for testing"""
    return izi_my_directive


@izi.directive(apply_globally=True)
def my_directive_global(default=None, **kwargs):
    """for testing"""
    return default


@izi.default_input_format('application/made-up', apply_globally=True)
def made_up_formatter_global(data):
    """for testing"""
    return data


@izi.default_output_format(apply_globally=True)
def output_formatter_global(data, request=None, response=None):
    """for testing"""
    return izi.output_format.json(data)


@izi.request_middleware()
def handle_request(request, response):
    """for testing"""
    return


@izi.startup()
def on_startup(api):
    """for testing"""
    return


@izi.static()
def static():
    """for testing"""
    return ('', )


@izi.sink('/all')
def sink(path):
    """for testing"""
    return path


@izi.exception(FakeException)
def handle_exception(exception):
    """Handles the provided exception for testing"""
    return True


@izi.not_found()
def not_found_handler():
    """for testing"""
    return True
