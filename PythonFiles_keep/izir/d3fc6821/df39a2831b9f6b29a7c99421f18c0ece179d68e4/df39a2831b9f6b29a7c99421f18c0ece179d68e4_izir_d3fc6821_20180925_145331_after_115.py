"""A simple example of a izi API call with versioning"""
import izi


@izi.get('/echo', versions=1)
def echo(text):
    return text


@izi.get('/echo', versions=range(2, 5))  # noqa
def echo(text):
    return 'Echo: {text}'.format(**locals())


@izi.get('/unversioned')
def hello():
    return 'Hello world!'


@izi.get('/echo', versions='6')
def echo(text):
    return 'Version 6'
