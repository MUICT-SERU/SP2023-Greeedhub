from biro import RestfulRouter as Router


def test_match():
    router = Router()
    router.append('GET', '/', 'handler4')
    router.append('GET', '/path', 'handler')
    router.append('POST', '/path', 'handler2')
    router.append('GET', '/error', 'handler3')
    handler, params = router.match('GET', '/path')
    assert params == {}
    assert handler == 'handler'
    handler, params = router.match('POST', '/path')
    assert params == {}
    assert handler == 'handler2'
    handler, params = router.match('GET', '/error')
    assert params == {}
    assert handler == 'handler3'
    handler, params = router.match('DELETE', '/path')
    assert params is None
    assert handler is None


def test_match_with_params():
    router = Router()
    router.append('GET', '/res/<key>:<value>', 'handler')
    handler, params = router.match('GET', '/res')
    assert params is None
    assert handler is None
    handler, params = router.match('GET', '/res/key:')
    assert params is None
    assert handler is None
    handler, params = router.match('GET', '/res/_k1:=v1')
    assert params == {"key": "_k1", "value": "=v1"}
    assert handler == 'handler'


def test_reverse():
    router = Router()
    router.append('GET', '/avatar/<id>.<ext>', 'handler')
    url = router.path_for('handler', id=13132, ext="png")
    assert '/avatar/13132.png' == url


def test_resource():
    from resources import article
    router = Router()
    router.resource('/article', article)

    url = router.path_for(article.show, article_id=117)
    assert '/article/117' == url


def test_resources():
    from resources import article
    router = Router()
    router.resources(article)

    url = router.path_for(article.show, article_id=191)
    assert '/article/191' == url
