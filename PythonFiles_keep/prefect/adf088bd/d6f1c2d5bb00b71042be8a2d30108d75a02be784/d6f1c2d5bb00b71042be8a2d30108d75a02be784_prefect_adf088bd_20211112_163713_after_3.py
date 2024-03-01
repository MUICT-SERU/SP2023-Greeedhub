from prefect.orion.database import dependencies
from prefect.orion.database.configurations import (
    DatabaseConfigurationBase,
    AsyncPostgresConfiguration,
    AioSqliteConfiguration,
)
from prefect.orion.database.query_components import (
    QueryComponentsBase,
    AsyncPostgresQueryComponents,
    AioSqliteQueryComponents,
)


async def test_injecting_an_existing_database_config():
    async with dependencies.temporary_db_config(AsyncPostgresConfiguration()):
        db = dependencies.provide_database_interface()
        assert type(db.config) == AsyncPostgresConfiguration

    async with dependencies.temporary_db_config(AioSqliteConfiguration()):
        db = dependencies.provide_database_interface()
        assert type(db.config) == AioSqliteConfiguration


async def test_injecting_a_really_dumb_database_config():
    class UselessConfiguration(DatabaseConfigurationBase):
        def run_migrations(self, base_model):
            ...

        async def engine(
            self,
            orm_metadata,
        ):
            ...

    async with dependencies.temporary_db_config(
        UselessConfiguration(connection_url=None)
    ):
        db = dependencies.provide_database_interface()
        assert type(db.config) == UselessConfiguration


async def test_injecting_existing_query_components():
    async with dependencies.temporary_query_components(AsyncPostgresQueryComponents()):
        db = dependencies.provide_database_interface()
        assert type(db.queries) == AsyncPostgresQueryComponents

    async with dependencies.temporary_query_components(AioSqliteQueryComponents()):
        db = dependencies.provide_database_interface()
        assert type(db.queries) == AioSqliteQueryComponents


async def test_injecting_really_dumb_query_components():
    class ReallyBrokenQueries(QueryComponentsBase):
        # --- dialect-specific SqlAlchemy bindings

        def insert(self, obj):
            ...

        def max(self, *values):
            ...

        # --- dialect-specific JSON handling

        def uses_json_strings(self) -> bool:
            ...

        def cast_to_json(self, json_obj):
            ...

        def build_json_object(self, *args):
            ...

        def json_arr_agg(self, json_array):
            ...

        # --- dialect-optimized subqueries

        def make_timestamp_intervals(
            self,
            start_time,
            end_time,
            interval,
        ):
            ...

        def set_state_id_on_inserted_flow_runs_statement(
            self,
            fr_model,
            frs_model,
            inserted_flow_run_ids,
            insert_flow_run_states,
        ):
            ...

    async with dependencies.temporary_query_components(ReallyBrokenQueries()):
        db = dependencies.provide_database_interface()
        assert type(db.queries) == ReallyBrokenQueries
