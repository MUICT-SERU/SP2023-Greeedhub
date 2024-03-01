from typing import List
from uuid import UUID

import sqlalchemy as sa
from fastapi import Body, Depends, HTTPException, Path, Response, status

from prefect.orion import models, schemas
from prefect.orion.api import dependencies
from prefect.orion.orchestration.rules import OrchestrationResult
from prefect.orion.utilities.server import OrionRouter

router = OrionRouter(prefix="/task_runs", tags=["Task Runs"])


@router.post("/")
async def create_task_run(
    task_run: schemas.actions.TaskRunCreate,
    response: Response,
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.core.TaskRun:
    """
    Create a task run
    """
    nested = await session.begin_nested()
    try:
        task_run = await models.task_runs.create_task_run(
            session=session, task_run=task_run
        )
        response.status_code = status.HTTP_201_CREATED
    except sa.exc.IntegrityError:
        await nested.rollback()
        query = sa.select(models.orm.TaskRun).where(
            sa.and_(
                models.orm.TaskRun.flow_run_id == task_run.flow_run_id,
                models.orm.TaskRun.task_key == task_run.task_key,
                models.orm.TaskRun.dynamic_key == task_run.dynamic_key,
            )
        )
        result = await session.execute(query)
        task_run = result.scalar()
    return task_run


@router.get("/{id}")
async def read_task_run(
    task_run_id: UUID = Path(..., description="The task run id", alias="id"),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.core.TaskRun:
    """
    Get a task run by id
    """
    task_run = await models.task_runs.read_task_run(
        session=session, task_run_id=task_run_id
    )
    if not task_run:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_run


@router.get("/")
async def read_task_runs(
    session: sa.orm.Session = Depends(dependencies.get_session),
    pagination: schemas.pagination.Pagination = Body(schemas.pagination.Pagination()),
    flows: schemas.filters.FlowFilter = None,
    flow_runs: schemas.filters.FlowRunFilter = None,
    task_runs: schemas.filters.TaskRunFilter = None,
) -> List[schemas.core.TaskRun]:
    """
    Query for task runs
    """
    return await models.task_runs.read_task_runs(
        session=session,
        flow_filter=flows,
        flow_run_filter=flow_runs,
        task_run_filter=task_runs,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_run(
    task_run_id: UUID = Path(..., description="The task run id", alias="id"),
    session: sa.orm.Session = Depends(dependencies.get_session),
):
    """
    Delete a task run by id
    """
    result = await models.task_runs.delete_task_run(
        session=session, task_run_id=task_run_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.post("/{id}/set_state")
async def set_task_run_state(
    task_run_id: UUID = Path(..., description="The task run id", alias="id"),
    state: schemas.actions.StateCreate = Body(..., description="The intended state."),
    session: sa.orm.Session = Depends(dependencies.get_session),
    response: Response = None,
) -> OrchestrationResult:
    """Set a task run state, invoking any orchestration rules."""

    # create the state
    orchestration_result = await models.task_run_states.orchestrate_task_run_state(
        session=session,
        task_run_id=task_run_id,
        state=state,
    )

    if orchestration_result.status == schemas.responses.SetStateStatus.WAIT:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_201_CREATED

    return orchestration_result
