import os
import uuid

from guillotina.interfaces import IContainer
from guillotina.transactions import get_transaction
from guillotina.utils import get_content_path, get_current_request
from pypika import PostgreSQLQuery as Query
from pypika import Table

aliases = Table('aliases')
links = Table('links')


async def get_links(ob):
    pass


async def update_links(ob, content):
    pass


async def get_aliases(ob):
    txn = get_transaction()
    query = Query.from_(aliases).select(
        aliases.alias_id, aliases.path, aliases.moved
    ).where(
        aliases.zoid == ob._p_oid
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        results = await conn.fetch(str(query))
    data = []
    for result in results:
        data.append({
            'id': result['alias_id'],
            'path': result['path'],
            'moved': result['moved']
        })
    return data


async def add_alias(ob, path, container=None):
    path = '/' + path.strip('/')
    txn = get_transaction()
    if container is None:
        req = get_current_request()
        container = req.container
    query = Query.into(aliases).columns(
        'alias_id', 'container_id', 'zoid', 'path', 'moved').insert(
        uuid.uuid4().hex,
        container._p_oid,
        ob._p_oid,
        path,
        True
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        await conn.execute(str(query))


async def remove_alias(ob, path):
    txn = get_transaction()
    query = Query.from_(aliases).where(
        aliases.zoid == ob._p_oid).where(
        aliases.path == path
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        await conn.execute(str(query.delete()))


async def get_inherited_aliases(ob):
    ids_to_lookup = {}
    context = ob
    while context is not None and not IContainer.providedBy(context):
        ids_to_lookup[context._p_oid] = context
        context = context.__parent__

    query = Query.from_(aliases).select(
        aliases.zoid, aliases.alias_id, aliases.path, aliases.moved
    ).where(
        aliases.zoid.isin(list(ids_to_lookup.keys()))
    )

    txn = get_transaction()
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        results = await conn.fetch(str(query))

    data = []
    ob_path = get_content_path(ob)
    for result in results:
        path = result['path']
        context = ids_to_lookup[result['zoid']]
        context_path = get_content_path(context)
        current_sub_path = ob_path[len(context_path):]
        path = os.path.join(path, current_sub_path.strip('/'))
        data.append({
            'id': result['alias_id'],
            'context_path': context_path,
            'path': path,
            'moved': result['moved']
        })
    return data


async def translate_links(txt):
    pass
