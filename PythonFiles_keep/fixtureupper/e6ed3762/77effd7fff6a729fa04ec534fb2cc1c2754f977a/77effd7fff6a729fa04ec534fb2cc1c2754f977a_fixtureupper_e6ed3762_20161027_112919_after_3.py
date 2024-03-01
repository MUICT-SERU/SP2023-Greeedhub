from fixtureupper.base import BaseFixtureUpper
from fixtureupper.model import ModelFixtureUpper
from fixtureupper.sqlalchemy import SqlAlchemyModelFixtureUpper


def UpperRegister(upper_type):
    if upper_type == 'Base':
        return type('BaseFixtureUpper', (BaseFixtureUpper,), {
            '_upper_classes': {},
        })
    elif upper_type == 'Model':
        return type('ModelFixtureUpper', (ModelFixtureUpper,), {
            '_upper_classes': {},
        })
    elif upper_type == 'SqlAlchemyModel':
        return type('SqlAlchemyModelFixtureUpper', (SqlAlchemyModelFixtureUpper,), {
            '_upper_classes': {},
        })
    raise RuntimeError
