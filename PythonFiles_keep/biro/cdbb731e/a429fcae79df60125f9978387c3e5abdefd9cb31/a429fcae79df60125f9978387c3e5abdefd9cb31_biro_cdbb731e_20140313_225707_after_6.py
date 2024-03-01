
from biro import get, path_for


def test_get():
    @get('/test/<id>')
    def test():
        pass

    assert path_for(test, id=309) == '/test/309'
