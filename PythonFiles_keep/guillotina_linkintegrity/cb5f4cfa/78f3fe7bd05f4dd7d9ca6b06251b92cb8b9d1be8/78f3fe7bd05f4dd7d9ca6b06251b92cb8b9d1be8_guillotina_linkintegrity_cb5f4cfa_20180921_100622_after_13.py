import json


async def test_redirect_after_content_renamed(container_requester):
    async with container_requester as requester:
        await requester('POST', '/db/guillotina', data=json.dumps({
            'id': 'foobar',
            '@type': 'Item'
        }))
        await requester('POST', '/db/guillotina/foobar/@move',
                        data=json.dumps({
                            'new_id': 'foobar2'
                        }))
        _, status = await requester(
            'GET', '/db/guillotina/foobar', allow_redirects=False)
        assert status == 301
