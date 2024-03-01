import datetime
from typing import List
from uuid import UUID

import pendulum
import sqlalchemy as sa
from sqlalchemy import delete, select

from prefect.orion import schemas
from prefect.orion.models import orm
from prefect.orion.orchestration.global_policy import update_run_details
from prefect.orion.utilities.database import dialect_specific_insert, get_dialect


async def create_deployment(
    session: sa.orm.Session,
    deployment: schemas.core.Deployment,
) -> orm.Deployment:
    """Upserts a deployment

    Args:
        session (sa.orm.Session): a database session
        deployment (schemas.core.Deployment): a deployment model

    Returns:
        orm.Deployment: the newly-created or updated deployment

    """
    insert_stmt = (
        dialect_specific_insert(orm.Deployment)
        .values(**deployment.dict(shallow=True, exclude_unset=True))
        .on_conflict_do_update(
            index_elements=["flow_id", "name"],
            set_=deployment.dict(
                shallow=True, include={"schedule", "is_schedule_active"}
            ),
        )
    )

    await session.execute(insert_stmt)

    query = (
        sa.select(orm.Deployment)
        .where(
            sa.and_(
                orm.Deployment.flow_id == deployment.flow_id,
                orm.Deployment.name == deployment.name,
            )
        )
        .execution_options(populate_existing=True)
    )
    result = await session.execute(query)
    model = result.scalar()

    return model


async def read_deployment(
    session: sa.orm.Session, deployment_id: UUID
) -> orm.Deployment:
    """Reads a deployment by id

    Args:
        session (sa.orm.Session): A database session
        deployment_id (str): a deployment id

    Returns:
        orm.Deployment: the deployment
    """
    return await session.get(orm.Deployment, deployment_id)


async def read_deployments(
    session: sa.orm.Session,
    offset: int = None,
    limit: int = None,
) -> List[orm.Deployment]:
    """Read deployments

    Args:
        session (sa.orm.Session): A database session
        offset (int): Query offset
        limit(int): Query limit

    Returns:
        List[orm.Deployment]: deployments
    """

    query = select(orm.Deployment).order_by(orm.Deployment.id)

    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    result = await session.execute(query)
    return result.scalars().unique().all()


async def delete_deployment(session: sa.orm.Session, deployment_id: UUID) -> bool:
    """Delete a deployment by id

    Args:
        session (sa.orm.Session): A database session
        deployment_id (str): a deployment id

    Returns:
        bool: whether or not the deployment was deleted
    """
    result = await session.execute(
        delete(orm.Deployment).where(orm.Deployment.id == deployment_id)
    )
    return result.rowcount > 0


async def schedule_runs(
    session: sa.orm.Session,
    deployment_id: UUID,
    start_time: datetime.datetime = None,
    end_time: datetime.datetime = None,
    max_runs: int = None,
):
    runs = await _generate_scheduled_flow_runs(
        session=session,
        deployment_id=deployment_id,
        start_time=start_time,
        end_time=end_time,
        max_runs=max_runs,
    )
    return await _insert_scheduled_flow_runs(session=session, runs=runs)


async def _generate_scheduled_flow_runs(
    session: sa.orm.Session,
    deployment_id: UUID,
    start_time: datetime.datetime = None,
    end_time: datetime.datetime = None,
    max_runs: int = None,
) -> List[schemas.core.FlowRun]:
    """
    Given a `deployment_id` and schedule, generates a list of flow run objects and
    associated scheduled states that represent scheduled flow runs. This method
    does NOT insert generated runs into the database, in order to facilitate
    batch operations. Call `_insert_scheduled_flow_runs()` to insert these runs.
    """

    if max_runs is None:
        max_runs = 100
    if start_time is None:
        start_time = pendulum.now("UTC")
    if end_time is None:
        end_time = pendulum.now("UTC").add(years=1)

    runs = []

    # retrieve the deployment
    deployment = await session.get(orm.Deployment, deployment_id)

    if not deployment:
        raise ValueError(f'No deployment found: "{deployment_id}"')

    dates = await deployment.schedule.get_dates(
        n=max_runs, start=start_time, end=end_time
    )

    for date in dates:
        run = schemas.core.FlowRun(
            flow_id=deployment.flow_id,
            deployment_id=deployment_id,
            # parameters=,
            idempotency_key=f"scheduled {deployment.id} {date}",
            tags=["auto-scheduled"],
            auto_scheduled=True,
            state=schemas.states.Scheduled(
                scheduled_time=date,
                message="Flow run scheduled",
            ),
        )
        # apply run details updates
        update_run_details(initial_state=None, proposed_state=run.state, run=run)
        runs.append(run)

    return runs


async def _insert_scheduled_flow_runs(
    session: sa.orm.Session,
    runs: List[schemas.core.FlowRun],
) -> List[schemas.core.FlowRun]:
    """
    Given a list of flow runs to schedule, as generated by `_generate_scheduled_flow_runs`,
    inserts them into the database. Note this is a separate method to facilitate batch
    operations on many scheduled runs.

    Returns a list of flow runs that were created
    """

    # gracefully insert the flow runs against the idempotency key
    # this syntax (insert statement, values to insert) is most efficient
    # because it uses a single bind parameter
    insert = dialect_specific_insert(orm.FlowRun)
    await session.execute(
        insert.on_conflict_do_nothing(index_elements=["flow_id", "idempotency_key"]),
        [r.dict(exclude={"created", "updated"}) for r in runs],
    )

    # query for the rows that were newly inserted (by checking for any flow runs with
    # no corresponding flow run states)
    inserted_rows = (
        sa.select(orm.FlowRun.id)
        .join(
            orm.FlowRunState,
            orm.FlowRun.id == orm.FlowRunState.flow_run_id,
            isouter=True,
        )
        .where(
            orm.FlowRun.id.in_([r.id for r in runs]),
            orm.FlowRunState.id.is_(None),
        )
    )
    inserted_flow_run_ids = (await session.execute(inserted_rows)).scalars().all()

    # insert flow run states that correspond to the newly-insert rows
    insert_flow_run_states = [
        {"flow_run_id": r.id, **r.state.dict(exclude={"created", "updated"})}
        for r in runs
        if r.id in inserted_flow_run_ids
    ]
    if insert_flow_run_states:
        # this syntax (insert statement, values to insert) is most efficient
        # because it uses a single bind parameter
        await session.execute(
            orm.FlowRunState.__table__.insert(), insert_flow_run_states
        )

        # set the `state_id` on the newly inserted runs
        if get_dialect().name == "postgresql":
            # postgres supports `UPDATE ... FROM` syntax
            stmt = (
                sa.update(orm.FlowRun)
                .where(orm.FlowRunState.flow_run_id == orm.FlowRun.id)
                .where(
                    orm.FlowRunState.id.in_([r["id"] for r in insert_flow_run_states])
                )
                .values(state_id=orm.FlowRunState.id)
                # no need to synchronize as these flow runs are entirely new
                .execution_options(synchronize_session=False)
            )
        else:
            # sqlite requires a correlated subquery to update from another table
            subquery = (
                sa.select(orm.FlowRunState.id)
                .where(
                    orm.FlowRunState.flow_run_id == orm.FlowRun.id,
                    orm.FlowRunState.id.in_([r["id"] for r in insert_flow_run_states]),
                )
                .limit(1)
                .scalar_subquery()
            )
            stmt = (
                sa.update(orm.FlowRun).values(state_id=subquery)
                # no need to synchronize as these flow runs are entirely new
                .execution_options(synchronize_session=False)
            )
        await session.execute(stmt)

    return [r for r in runs if r.id in inserted_flow_run_ids]
