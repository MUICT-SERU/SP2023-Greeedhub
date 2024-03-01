import os
import sqlalchemy as sa
import sqlite3

from abc import ABC, abstractmethod, abstractproperty
from sqlalchemy.ext.asyncio import create_async_engine


class DatabaseConfigurationBase(ABC):
    """
    Abstract base class used to inject database-specific configuration into Orion.
    """

    def __init__(self, connection_url=None):
        self.connection_url = connection_url

    def _unique_key(self):
        """
        Returns a key used to determine whether to instantiate a new DB interface.
        """
        return str(self.__class__) + "_" + str(self.connection_url)

    @abstractproperty
    def base_model_mixins(self) -> list:
        """A list of ORM mixins used to extend core Orion models"""

    @abstractmethod
    def run_migrations(self, base_model):
        """Database-specific migration configuration"""

    @abstractmethod
    async def engine(
        self,
        echo,
        timeout,
        orm_metadata,
    ) -> sa.engine.Engine:
        """Returns a SqlAlchemy engine"""


class AsyncPostgresConfiguration(DatabaseConfigurationBase):
    # TODO - validate connection url for postgres and asyncpg driver

    @property
    def base_model_mixins(self):
        return []

    def run_migrations(self, base_model):
        ...

    async def engine(
        self,
        echo,
        timeout,
        orm_metadata,
    ) -> sa.engine.Engine:
        """Retrieves an async SQLAlchemy engine.

        Args:
            connection_url (str, optional): The database connection string.
                Defaults to the value in Prefect's settings.
            echo (bool, optional): Whether to echo SQL sent
                to the database. Defaults to the value in Prefect's settings.
            timeout (float, optional): The database statement timeout, in seconds

        Returns:
            sa.engine.Engine: a SQLAlchemy engine
        """
        kwargs = dict()

        # apply database timeout
        if timeout is not None:
            kwargs["connect_args"] = dict(command_timeout=timeout)

        return create_async_engine(self.connection_url, echo=echo, **kwargs)


class AioSqliteConfiguration(DatabaseConfigurationBase):
    # TODO - validate connection url for sqlite and driver

    MIN_SQLITE_VERSION = (3, 24, 0)

    def run_migrations(self, base_model):
        ...

    @property
    def base_model_mixins(self):
        return []

    async def engine(
        self,
        echo,
        timeout,
        orm_metadata,
    ) -> sa.engine.Engine:
        """Retrieves an async SQLAlchemy engine.

        If a sqlite in-memory database OR a non-existant sqlite file-based database
        is provided, it is automatically populated with database objects.

        Args:
            connection_url (str, optional): The database connection string.
                Defaults to the value in Prefect's settings.
            echo (bool, optional): Whether to echo SQL sent
                to the database. Defaults to the value in Prefect's settings.
            timeout (float, optional): The database statement timeout, in seconds

        Returns:
            sa.engine.Engine: a SQLAlchemy engine
        """
        kwargs = {}

        # apply database timeout
        if timeout is not None:
            kwargs["connect_args"] = dict(timeout=timeout)

        # ensure a long-lasting pool is used with in-memory databases
        # because they disappear when the last connection closes
        if ":memory:" in self.connection_url:
            kwargs.update(poolclass=sa.pool.SingletonThreadPool)

        engine = create_async_engine(self.connection_url, echo=echo, **kwargs)
        sa.event.listen(engine.sync_engine, "engine_connect", self.setup_sqlite)

        if sqlite3.sqlite_version_info < self.MIN_SQLITE_VERSION:
            required = ".".join(str(v) for v in self.MIN_SQLITE_VERSION)
            raise RuntimeError(
                f"Orion requires sqlite >= {required} but we found version "
                f"{sqlite3.sqlite_version}"
            )

        # if this is a new sqlite database create all database objects
        if (
            ":memory:" in engine.url.database
            or "mode=memory" in engine.url.database
            or not os.path.exists(engine.url.database)
        ):
            async with engine.begin() as conn:
                await conn.run_sync(orm_metadata.create_all)

        return engine

    def setup_sqlite(self, conn, named=True):
        """Issue PRAGMA statements to SQLITE on connect. PRAGMAs only last for the
        duration of the connection. See https://www.sqlite.org/pragma.html for more info."""
        # enable foreign keys
        conn.execute(sa.text("PRAGMA foreign_keys = ON;"))

        # write to a write-ahead-log instead and regularly
        # commit the changes
        # this allows multiple concurrent readers even during
        # a write transaction
        conn.execute(sa.text("PRAGMA journal_mode = WAL;"))

        # wait for this amount of time while a table is locked
        # before returning and rasing an error
        # setting the value very high allows for more 'concurrency'
        # without running into errors, but may result in slow api calls
        conn.execute(sa.text("PRAGMA busy_timeout = 60000;"))  # 60s
        conn.commit()
