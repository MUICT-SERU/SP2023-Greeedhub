import izi

from demo.authentication import basic_authentication
from demo.directives import SqlalchemySession
from demo.models import TestUser, TestModel
from demo.validation import CreateUserSchema, DumpSchema, unique_username


@izi.post('/create_user2', requires=basic_authentication)
def create_user2(
    db: SqlalchemySession,
    data: CreateUserSchema()
):
    user = TestUser(
        **data
    )
    db.add(user)
    db.flush()
    return dict()


@izi.post('/create_user', requires=basic_authentication)
def create_user(
    db: SqlalchemySession,
    username: unique_username,
    password: izi.types.text
):
    user = TestUser(
        username=username,
        password=password
    )
    db.add(user)
    db.flush()
    return dict()


@izi.get('/test')
def test():
    return ''


@izi.get('/hello')
def make_simple_query(db: SqlalchemySession):
    for word in ["hello", "world", ":)"]:
        test_model = TestModel()
        test_model.name = word
        db.add(test_model)
        db.flush()
    return " ".join([obj.name for obj in db.query(TestModel).all()])


@izi.get('/hello2')
def transform_example(db: SqlalchemySession) -> DumpSchema():
    for word in ["hello", "world", ":)"]:
        test_model = TestModel()
        test_model.name = word
        db.add(test_model)
        db.flush()
    return dict(users=db.query(TestModel).all())


@izi.get('/protected', requires=basic_authentication)
def protected():
    return 'smile :)'
