from jsonmodels.models import Base


class Model(Base):
    """A base class for declared model class.

    This class should not be instantiated directly.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tablename = getattr(self, "__tablename__", None)
        self.__tablename__ = tablename or self.__class__.__name__.lower()

    def __repr__(self):  # pragma: no cover
        return f"<{self.__class__.__name__}: __tablename__={self.__tablename__}>"
