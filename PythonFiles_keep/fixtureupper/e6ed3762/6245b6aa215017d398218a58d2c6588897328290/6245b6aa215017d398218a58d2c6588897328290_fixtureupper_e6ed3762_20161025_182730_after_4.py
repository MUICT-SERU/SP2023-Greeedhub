from fixtureupper.base import BaseFixtureUpper
from fixtureupper.model import ModelFixtureUpper
from fixtureupper.sqlalchemy import SqlAlchemyModelFixtureUpper


def UpperRegister(upper_type):
    if upper_type == 'Base':
        return type('BaseFixtureUpper', (BaseFixtureUpper,), {
            '_generator_classes': {},
        })
    elif upper_type == 'Model':
        return type('ModelFixtureUpper', (ModelFixtureUpper,), {
            '_generator_classes': {},
        })
    elif upper_type == 'SqlAlchemyModel':
        return type('SqlAlchemyModelFixtureUpper', (SqlAlchemyModelFixtureUpper,), {
            '_generator_classes': {},
        })
    raise RuntimeError
