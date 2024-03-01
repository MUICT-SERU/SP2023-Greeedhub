"""Simple 1 endpoint Fake IZIR API module usable for testing importation of modules"""
import izi


class FakeSimpleException(Exception):
    pass

@izi.get()
def made_up_hello():
    """for science!"""
    return 'hello'

@izi.get('/exception')
def made_up_exception():
    raise FakeSimpleException('test')
