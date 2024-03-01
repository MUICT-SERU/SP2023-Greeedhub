from guillotina_linkintegrity import utils
from guillotina.content import create_content_in_container


async def test_add_alias(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            foobar = await create_content_in_container(
                container, 'Item', id_='foobar')
            await txn.commit()  # writes out content
            await utils.add_alias(foobar, '/foobar2', container)

            aliases = await utils.get_aliases(foobar)
            assert len(aliases) == 1
            assert aliases[0]['path'] == '/foobar2'


async def test_remove_alias(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            foobar = await create_content_in_container(
                container, 'Item', id_='foobar')
            await txn.commit()  # writes out content
            await utils.add_alias(foobar, '/foobar2', container)
            await utils.add_alias(foobar, '/foobar3', container)

            aliases = await utils.get_aliases(foobar)
            assert len(aliases) == 2

            await utils.remove_alias(foobar, '/foobar2')

            aliases = await utils.get_aliases(foobar)
            assert len(aliases) == 1
            assert aliases[0]['path'] == '/foobar3'


async def test_get_inherited_aliases(guillotina, container_requester):
    async with container_requester:
        async with guillotina.transaction() as txn:
            root = await txn.manager.get_root()
            container = await root.async_get('guillotina')
            folder = await create_content_in_container(
                container, 'Folder', id_='folder')
            item = await create_content_in_container(
                folder, 'Item', id_='item')
            await txn.commit()  # writes out content
            await utils.add_alias(folder, '/other', container)

            assert len(await utils.get_aliases(folder)) == 1
            assert len(await utils.get_aliases(item)) == 0

            aliases = await utils.get_inherited_aliases(item)
            assert len(aliases) == 1
            assert aliases[0]['path'] == '/other/item'
