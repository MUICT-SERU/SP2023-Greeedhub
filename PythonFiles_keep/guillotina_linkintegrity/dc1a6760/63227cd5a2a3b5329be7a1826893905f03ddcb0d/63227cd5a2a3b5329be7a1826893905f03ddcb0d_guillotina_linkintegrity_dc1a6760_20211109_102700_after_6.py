import json
import pytest
import os

pytestmark = pytest.mark.asyncio


NOT_POSTGRES = os.environ.get("DATABASE", "DUMMY") in ("cockroachdb", "DUMMY")
PG_CATALOG_SETTINGS = {
    "applications": ["guillotina.contrib.catalog.pg"],
    "load_utilities": {
        "catalog": {
            "provides": "guillotina.interfaces.ICatalogUtility",
            "factory": "guillotina.contrib.catalog.pg.utility.PGSearchUtility",
        }
    },
}


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_redirect_after_content_renamed(
        redis_container, container_requester):
    async with container_requester as requester:
        await requester('POST', '/db/guillotina', data=json.dumps({
            'id': 'foobar',
            '@type': 'Item'
        }))
        resp, status = await requester(
            'POST', '/db/guillotina/foobar/@move',
            data=json.dumps({
                'new_id': 'foobar2'
            }))
        assert status == 200
        _, status = await requester(
            'GET', '/db/guillotina/foobar', allow_redirects=False)
        assert status == 301

        _, status = await requester(
            'GET', '/db/guillotina/foobar/@ids', allow_redirects=False)
        assert status == 301


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_api_aliases(redis_container, container_requester):
    async with container_requester as requester:
        await requester('POST', '/db/guillotina', data=json.dumps({
            'id': 'foo',
            '@type': 'Folder'
        }))
        await requester('POST', '/db/guillotina/foo', data=json.dumps({
            'id': 'bar',
            '@type': 'Item'
        }))
        resp, _ = await requester('GET', '/db/guillotina/foo/bar/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 0

        await requester(
            'PATCH', '/db/guillotina/foo/@aliases',
            data=json.dumps({
                'paths': ['/foo2']
            }))
        await requester(
            'PATCH', '/db/guillotina/foo/bar/@aliases',
            data=json.dumps({
                'paths': ['/foobar']
            }))

        resp, _ = await requester('GET', '/db/guillotina/foo/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 1

        # not from move so should *not* inherit
        resp, _ = await requester('GET', '/db/guillotina/foo/bar/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 1

        await requester(
            'DELETE', '/db/guillotina/foo/@aliases',
            data=json.dumps({
                'paths': ['/foo2']
            }))
        await requester(
            'DELETE', '/db/guillotina/foo/bar/@aliases',
            data=json.dumps({
                'paths': ['/foobar']
            }))

        resp, _ = await requester('GET', '/db/guillotina/foo/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 0

        # not from move so should *not* inherit
        resp, _ = await requester('GET', '/db/guillotina/foo/bar/@aliases')
        assert len(resp['inherited']) == 0
        assert len(resp['aliases']) == 0
