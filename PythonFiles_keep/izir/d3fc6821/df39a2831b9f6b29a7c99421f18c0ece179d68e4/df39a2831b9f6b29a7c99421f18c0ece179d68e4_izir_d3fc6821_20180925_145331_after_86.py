import izi


@izi.get()
def hello_world():
    return 'Hello world!'


@izi.not_found()
def not_found():
    return {'Nothing': 'to see'}
