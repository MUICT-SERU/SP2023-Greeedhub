import datetime
from typing import List

import pendulum
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from prefect import settings
from prefect.orion import models, schemas
from prefect.orion.models import orm
from prefect.orion.schemas import states
from prefect.orion.orchestration.rules import (
    FlowOrchestrationContext,
    TaskOrchestrationContext,
)
from prefect.orion.utilities.database import (
    ENGINES,
    Base,
    get_engine,
    get_session_factory,
)


@pytest.fixture(scope="session", autouse=True)
async def database_engine():
    """Produce a database engine"""
    engine = await get_engine()
    try:
        yield engine
    finally:
        await engine.dispose()
        ENGINES.clear()


@pytest.fixture
def print_query(database_engine):
    def inner(query):
        return print(query.compile(database_engine))

    return inner


@pytest.fixture(scope="session", autouse=True)
async def setup_db(database_engine):
    """Create all database objects prior to running tests, and drop them when tests are done."""
    try:
        # build the database
        async with database_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield

    finally:
        # tear down the databse
        async with database_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clear_db(database_engine):
    """Clear the database by

    Args:
        database_engine ([type]): [description]
    """
    yield
    async with database_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def session(database_engine) -> AsyncSession:
    session_factory = await get_session_factory(bind=database_engine)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def flow(session) -> models.orm.Flow:
    model = await models.flows.create_flow(
        session=session, flow=schemas.actions.FlowCreate(name="my-flow")
    )
    await session.commit()
    return model


@pytest.fixture
async def flow_run(session, flow) -> models.orm.FlowRun:
    model = await models.flow_runs.create_flow_run(
        session=session,
        flow_run=schemas.actions.FlowRunCreate(flow_id=flow.id, flow_version="0.1"),
    )
    await session.commit()
    return model


@pytest.fixture
async def task_run(session, flow_run) -> models.orm.TaskRun:
    fake_task_run = schemas.actions.TaskRunCreate(
        flow_run_id=flow_run.id, task_key="my-key"
    )
    model = await models.task_runs.create_task_run(
        session=session,
        task_run=fake_task_run,
    )
    await session.commit()
    return model


@pytest.fixture
async def flow_run_states(session, flow_run) -> List[models.orm.FlowRunState]:
    scheduled_state = schemas.states.State(
        type=schemas.states.StateType.SCHEDULED,
        timestamp=pendulum.now("UTC").subtract(seconds=5),
        state_details=dict(scheduled_time=pendulum.now("UTC").subtract(seconds=1)),
    )
    scheduled_flow_run_state = (
        await models.flow_run_states.orchestrate_flow_run_state(
            session=session,
            flow_run_id=flow_run.id,
            state=scheduled_state,
        )
    ).state
    running_state = schemas.states.Running()
    running_flow_run_state = (
        await models.flow_run_states.orchestrate_flow_run_state(
            session=session,
            flow_run_id=flow_run.id,
            state=running_state,
        )
    ).state
    await session.commit()
    return [scheduled_flow_run_state, running_flow_run_state]


@pytest.fixture
async def task_run_states(session, task_run) -> List[models.orm.TaskRunState]:
    scheduled_state = schemas.states.State(
        type=schemas.states.StateType.SCHEDULED,
        timestamp=pendulum.now("UTC").subtract(seconds=5),
    )
    scheduled_task_run_state = (
        await models.task_run_states.orchestrate_task_run_state(
            session=session,
            task_run_id=task_run.id,
            state=scheduled_state,
        )
    ).state
    running_state = schemas.states.Running()
    running_task_run_state = (
        await models.task_run_states.orchestrate_task_run_state(
            session=session,
            task_run_id=task_run.id,
            state=running_state,
        )
    ).state
    await session.commit()
    return [scheduled_task_run_state, running_task_run_state]


@pytest.fixture
async def deployment(session, flow) -> models.orm.Deployment:
    deployment = await models.deployments.create_deployment(
        session=session,
        deployment=schemas.core.Deployment(
            name="My Deployment",
            flow_id=flow.id,
            schedule=schemas.schedules.IntervalSchedule(
                interval=datetime.timedelta(days=1)
            ),
        ),
    )
    await session.commit()
    return deployment


async def commit_task_run_state(
    session, task_run, state_type: states.StateType, state_details=None
):
    if state_type is None:
        return None
    state_details = dict() if state_details is None else state_details

    if (
        state_type == states.StateType.SCHEDULED
        and "scheduled_time" not in state_details
    ):
        state_details.update({"scheduled_time": pendulum.now()})

    new_state = schemas.actions.StateCreate(
        type=state_type,
        timestamp=pendulum.now("UTC").subtract(seconds=5),
        state_details=state_details,
    )

    orm_state = orm.TaskRunState(
        task_run_id=task_run.id,
        **new_state.dict(shallow=True),
    )

    session.add(orm_state)
    await session.flush()
    return orm_state.as_state()


async def commit_flow_run_state(
    session, flow_run, state_type: states.StateType, state_details=None
):
    if state_type is None:
        return None
    state_details = dict() if state_details is None else state_details

    if (
        state_type == states.StateType.SCHEDULED
        and "scheduled_time" not in state_details
    ):
        state_details.update({"scheduled_time": pendulum.now()})

    new_state = schemas.actions.StateCreate(
        type=state_type,
        timestamp=pendulum.now("UTC").subtract(seconds=5),
        state_details=state_details,
    )

    orm_state = orm.FlowRunState(
        flow_run_id=flow_run.id,
        **new_state.dict(shallow=True),
    )

    session.add(orm_state)
    await session.flush()
    return orm_state.as_state()


@pytest.fixture
def initialize_orchestration(
    task_run,
    flow_run,
):
    async def initializer(
        session,
        run_type,
        initial_state_type,
        proposed_state_type,
        initial_details=None,
        proposed_details=None,
    ):

        if run_type == "flow":
            run = flow_run
            context = FlowOrchestrationContext
            state_constructor = commit_flow_run_state
        elif run_type == "task":
            run = task_run
            context = TaskOrchestrationContext
            state_constructor = commit_task_run_state

        initial_state = await state_constructor(
            session,
            run,
            initial_state_type,
            initial_details,
        )

        proposed_details = proposed_details if proposed_details else dict()
        psd = states.StateDetails(**proposed_details)
        proposed_state = states.State(type=proposed_state_type, state_details=psd)

        ctx = context(
            initial_state=initial_state,
            proposed_state=proposed_state,
            session=session,
            run=run,
            run_id=run.id,
        )

        return ctx

    return initializer
