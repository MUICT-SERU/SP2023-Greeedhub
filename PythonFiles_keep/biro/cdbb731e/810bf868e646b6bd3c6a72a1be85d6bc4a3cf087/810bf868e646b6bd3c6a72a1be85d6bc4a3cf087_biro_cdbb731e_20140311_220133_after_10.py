
from biro import get, path_for, resource, match, method


def test_get():
    @get('/test/<id>')
    def test():
        pass

    assert path_for(test, id=309) == '/test/309'


def test_rest():

    @resource('/v1/article')
    class Article:
        def show(article_id):
            pass

        def create():
            pass

        @method('patch')
        def like(article_id):
            pass

    assert match('GET', '/v1/article/107') == (Article.show, {'article_id': '107'})
