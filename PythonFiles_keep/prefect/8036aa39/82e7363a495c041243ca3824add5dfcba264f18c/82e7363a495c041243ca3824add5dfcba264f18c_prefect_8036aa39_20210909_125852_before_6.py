import datetime
from typing import Dict, List, Union
from uuid import UUID

from pydantic import Field

from prefect.orion import schemas
from prefect.orion.utilities.functions import ParameterSchema
from prefect.orion.utilities.schemas import ORMBaseModel, PrefectBaseModel


class Flow(ORMBaseModel):
    name: str = Field(..., example="my-flow")
    tags: List[str] = Field(default_factory=list, example=["tag-1", "tag-2"])

    # relationships
    # flow_runs: List["FlowRun"] = Field(default_factory=list)
    # deployments: List["Deployment"] = Field(default_factory=list)


class RunDetails(PrefectBaseModel):
    state_id: UUID = None
    state_type: schemas.states.StateType = None
    run_count: int = 0

    # the expected start time is set the first time
    # the run is placed in a state
    expected_start_time: datetime.datetime = None

    # the next scheduled start time will be populated
    # whenever the run is in a scheduled state
    next_scheduled_start_time: datetime.datetime = None
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None
    total_run_time_seconds: float = 0.0
    total_time_seconds: float = 0.0


class FlowRunDetails(RunDetails):
    auto_scheduled: bool = False


class TaskRunDetails(RunDetails):
    pass


class FlowRun(ORMBaseModel):
    flow_id: UUID
    state_id: UUID = None
    deployment_id: UUID = None
    flow_version: str = Field(None, example="1.0")
    parameters: dict = Field(default_factory=dict)
    idempotency_key: str = None
    context: dict = Field(default_factory=dict, example={"my_var": "my_val"})
    empirical_policy: dict = Field(default_factory=dict)
    empirical_config: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list, example=["tag-1", "tag-2"])
    parent_task_run_id: UUID = None
    run_details: FlowRunDetails = Field(default_factory=FlowRunDetails)

    # relationships
    # flow: Flow = None
    # task_runs: List["TaskRun"] = Field(default_factory=list)
    state: schemas.states.State = None
    # parent_task_run: "TaskRun" = None


class TaskRunPolicy(PrefectBaseModel):
    max_retries: int = 0
    retry_delay_seconds: float = 0


class TaskRun(ORMBaseModel):
    flow_run_id: UUID
    task_key: str
    dynamic_key: str = None
    cache_key: str = None
    cache_expiration: datetime.datetime = None
    task_version: str = None
    empirical_policy: TaskRunPolicy = Field(default_factory=TaskRunPolicy)
    tags: List[str] = Field(default_factory=list, example=["tag-1", "tag-2"])
    state_id: UUID = None
    task_inputs: ParameterSchema = Field(default_factory=ParameterSchema)
    upstream_task_run_ids: Dict[str, UUID] = Field(default_factory=dict)
    run_details: TaskRunDetails = Field(default_factory=TaskRunDetails)

    # relationships
    # flow_run: FlowRun = None
    # subflow_runs: List[FlowRun] = Field(default_factory=list)
    state: schemas.states.State = None


class Deployment(ORMBaseModel):
    name: str
    flow_id: UUID
    schedule: Union[
        schemas.schedules.IntervalSchedule,
        schemas.schedules.CronSchedule,
    ] = None
    is_schedule_active: bool = True
    # flow: Flow = None


Flow.update_forward_refs()
FlowRun.update_forward_refs()
