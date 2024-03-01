from guillotina import configure
from guillotina.interfaces import IResource


@configure.service(method='GET', name='@aliases', context=IResource,
                   permission='guillotina.AccessContent')
async def get_aliases(context, request):
    '''
    Get ones directly on content AND inherited ones
    '''
    return {
        'foo': 'bar'
    }


@configure.service(method='PATCH', name='@aliases', context=IResource,
                   permission='guillotina.ModifyContent')
async def patch_aliases(context, request):
    pass


@configure.service(method='PUT', name='@aliases', context=IResource,
                   permission='guillotina.ModifyContent')
async def put_aliases(context, request):
    pass
