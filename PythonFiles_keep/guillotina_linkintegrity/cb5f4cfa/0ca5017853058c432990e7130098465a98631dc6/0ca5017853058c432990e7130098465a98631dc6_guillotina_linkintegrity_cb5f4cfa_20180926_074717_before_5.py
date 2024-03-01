import os

from guillotina.interfaces import IContainer
from guillotina.transactions import get_transaction
from guillotina.utils import (get_content_path, get_current_request,
                              get_object_url)
from lxml import html
from pypika import PostgreSQLQuery as Query
from pypika import Table

aliases_table = Table('aliases')
links_table = Table('links')
objects_table = Table('objects')


async def get_aliases(ob):
    txn = get_transaction()
    query = Query.from_(aliases_table).select(
        aliases_table.path, aliases_table.moved
    ).where(
        aliases_table.zoid == ob._p_oid
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        results = await conn.fetch(str(query))
    data = []
    for result in results:
        data.append({
            'path': result['path'],
            'moved': result['moved']
        })
    return data


async def add_aliases(ob, paths: list, container=None, moved=True):
    if container is None:
        req = get_current_request()
        container = req.container
    txn = get_transaction()
    query = Query.into(aliases_table).columns(
        'zoid', 'container_id', 'path', 'moved')
    for path in paths:
        path = '/' + path.strip('/')
        query = query.insert(
            ob._p_oid,
            container._p_oid,
            path,
            moved
        )

    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        await conn.execute(str(query))


async def remove_aliases(ob, paths: list):
    txn = get_transaction()
    for path in paths:
        query = Query.from_(aliases_table).where(
            (aliases_table.zoid == ob._p_oid) &
            (aliases_table.path == path)
        )
        storage = txn.manager._storage
        async with storage._pool.acquire() as conn:
            await conn.execute(str(query.delete()))


async def get_inherited_aliases(ob):
    ids_to_lookup = {}
    context = ob.__parent__
    while context is not None and not IContainer.providedBy(context):
        ids_to_lookup[context._p_oid] = context
        context = context.__parent__

    if len(ids_to_lookup) == 0:
        return []

    query = Query.from_(aliases_table).select(
        aliases_table.zoid, aliases_table.path, aliases_table.moved
    ).where(
        aliases_table.zoid.isin(list(ids_to_lookup.keys())) &
        aliases_table.moved == True  # noqa
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
            'context_path': context_path,
            'path': path,
            'moved': result['moved']
        })
    return data


async def get_links(ob):
    txn = get_transaction()
    query = Query.from_(links_table).select(
        links_table.target_id
    ).where(
        links_table.source_id == ob._p_oid
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        results = await conn.fetch(str(query))
    data = []
    for result in results:
        data.append(result['target_id'])
    return data


async def add_links(ob, links):
    txn = get_transaction()
    query = Query.into(links_table).columns('source_id', 'target_id')
    for link in links:
        query = query.insert(str(ob._p_oid), str(link._p_oid))
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        await conn.execute(str(query))


async def remove_links(ob, links):
    txn = get_transaction()
    query = Query.from_(links_table).where(
        (links_table.source_id == ob._p_oid) &
        links_table.target_id.isin([l._p_oid for l in links])
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        await conn.execute(str(query.delete()))


async def update_links_from_html(ob, *contents):
    links = set()
    for content in contents:
        dom = html.fromstring(content)
        for node in dom.xpath('//a') + dom.xpath('//img'):
            url = node.get('href', node.get('src', ''))
            if 'resolveuid/' not in url:
                continue
            _, _, uid = url.partition('resolveuid/')
            uid = uid.split('/')[0].split('?')[0]
            links.add(uid)

    txn = get_transaction()
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        # make sure to filter out bad links
        existing_oids = set()
        results = await conn.fetch(str(
            Query.from_(objects_table).select('zoid').where(
                objects_table.zoid.isin(list(links))
            )))
        for record in results:
            existing_oids.add(record['zoid'])

        # first delete all existing ones
        await conn.execute(str(Query.from_(links_table).where(
            links_table.source_id == ob._p_oid
        ).delete()))

        # then, readd
        links = links & existing_oids
        if len(links) > 0:
            query = Query.into(links_table).columns('source_id', 'target_id')
            for link in links:
                query = query.insert(str(ob._p_oid), link)

            await conn.execute(str(query))


async def translate_links(content, container=None):
    '''
    optimized url builder here so we don't pull
    full objects from database however, we lose caching.

    Would be great to move this into an implementation
    that worked with current cache/invalidation strategies
    '''
    req = None
    if container is None:
        req = get_current_request()
        container = req.container
    container_url = get_object_url(container, req)
    dom = html.fromstring(content)
    contexts = {}

    txn = get_transaction()
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        for node in dom.xpath('//a') + dom.xpath('//img'):
            url = node.get('href', node.get('src', ''))
            if 'resolveuid/' not in url:
                continue
            path = []
            _, _, current_uid = url.partition('resolveuid/')
            current_uid = current_uid.split('/')[0].split('?')[0]

            error = False
            while current_uid != container._p_oid:
                if current_uid not in contexts:
                    # fetch from db
                    result = await conn.fetch(str(
                        Query.from_(objects_table).select(
                            'id', 'parent_id').where(
                            objects_table.zoid == current_uid)))
                    if len(result) > 0:
                        contexts[current_uid] = {
                            'id': result[0]['id'],
                            'parent': result[0]['parent_id']
                        }
                    else:
                        # could not find, this should not happen
                        error = True
                        break
                path = [contexts[current_uid]['id']] + path
                current_uid = contexts[current_uid]['parent']

            if error:
                continue
            url = os.path.join(container_url, '/'.join(path))
            attr = node.tag.lower() == 'a' and 'href' or 'src'
            node.attrib[attr] = url

    return html.tostring(dom).decode('utf-8')
