import izi

from demo import api
from demo.base import Base
from demo.context import SqlalchemyContext, engine
from demo.directives import SqlalchemySession
from demo.models import TestUser


@izi.context_factory()
def create_context(*args, **kwargs):
    return SqlalchemyContext()


@izi.delete_context()
def delete_context(context: SqlalchemyContext, exception=None, errors=None, lacks_requirement=None):
    context.cleanup(exception)


@izi.local(skip_directives=False)
def initialize(db: SqlalchemySession):
    admin = TestUser(username='admin', password='admin')
    db.add(admin)
    db.flush()


@izi.extend_api()
def apis():
    return [api]


Base.metadata.create_all(bind=engine)
initialize()
