import izi


@izi.get()
def hello(request):
    """Says hellos"""
    return 'Hello Worlds for Bacon?!'
