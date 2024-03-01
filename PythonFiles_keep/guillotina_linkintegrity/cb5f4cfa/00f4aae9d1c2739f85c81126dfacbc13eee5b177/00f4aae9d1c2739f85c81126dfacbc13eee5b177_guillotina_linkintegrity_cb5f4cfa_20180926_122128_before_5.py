import os

from guillotina import configure
from guillotina.interfaces import (IObjectMovedEvent, IResource,
                                   ITraversalMissEvent)
from guillotina.response import HTTPMovedPermanently
from guillotina.transactions import get_transaction
from guillotina.utils import (execute, get_content_path, get_object_by_oid,
                              get_object_url)
from guillotina_linkintegrity import utils
from pypika import PostgreSQLQuery as Query
from pypika import Table

aliases_table = Table('aliases')


@configure.subscriber(for_=(IResource, IObjectMovedEvent))
async def object_moved(ob, event):
    parent_path = get_content_path(event.old_parent)
    old_path = os.path.join(parent_path, event.old_name)
    execute.before_commit(
        utils.add_aliases, ob, [old_path], moved=True)


@configure.subscriber(for_=ITraversalMissEvent)
async def check_content_moved(event):
    request = event.request
    if getattr(request, 'container', None) is None:
        return

    tail, _, view = '/'.join(event.tail).partition('/@')
    if view:
        view = '@' + view
    path = os.path.join(
        get_content_path(request.resource), tail)

    txn = get_transaction()
    query = Query.from_(aliases_table).select(
        aliases_table.zoid
    ).where(
        (aliases_table.path == path) |
        (aliases_table.path == path + '/' + view)
    )
    storage = txn.manager._storage
    async with storage._pool.acquire() as conn:
        results = await conn.fetch(str(query))

    if len(results) > 0:
        ob = await get_object_by_oid(results[0]['zoid'])
        url = get_object_url(ob)
        if view:
            url += '/' + view
        raise HTTPMovedPermanently(url)
