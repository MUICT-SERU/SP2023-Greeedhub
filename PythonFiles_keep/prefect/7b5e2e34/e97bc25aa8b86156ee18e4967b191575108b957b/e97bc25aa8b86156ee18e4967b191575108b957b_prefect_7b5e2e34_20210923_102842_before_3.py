from prefect.orion import models
from prefect.orion.orchestration.policies import BaseOrchestrationPolicy
from prefect.orion.orchestration.rules import (
    BaseUniversalRule,
    OrchestrationContext,
)

COMMON_GLOBAL_RULES = lambda: [
    SetRunStateType,
    SetStartTime,
    SetEndTime,
    IncrementRunCount,
    IncrementRunTime,
    SetExpectedStartTime,
    SetNextScheduledStartTime,
]


class GlobalFlowPolicy(BaseOrchestrationPolicy):
    def priority():
        return COMMON_GLOBAL_RULES() + [UpdateSubflowParentTask]


class GlobalTaskPolicy(BaseOrchestrationPolicy):
    def priority():
        return COMMON_GLOBAL_RULES()


class SetRunStateType(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:

        # record the new state's type
        context.run.state_type = context.proposed_state.type


class SetStartTime(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:
        # if entering a running state and no start time is set...
        if context.proposed_state.is_running() and context.run.start_time is None:
            # set the start time
            context.run.start_time = context.proposed_state.timestamp


class SetEndTime(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:
        # if exiting a final state for a non-final state...
        if (
            context.initial_state
            and context.initial_state.is_final()
            and not context.proposed_state.is_final()
        ):
            # clear the end time
            context.run.end_time = None

        # if entering a final state...
        if context.proposed_state.is_final():
            # if the run has a start time and no end time, give it one
            if context.run.start_time and not context.run.end_time:
                context.run.end_time = context.proposed_state.timestamp


class IncrementRunTime(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:
        # if exiting a running state...
        if context.initial_state and context.initial_state.is_running():
            # increment the run time by the time spent in the previous state
            context.run.total_run_time += (
                context.proposed_state.timestamp - context.initial_state.timestamp
            )


class IncrementRunCount(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:
        # if entering a running state...
        if context.proposed_state.is_running():
            # increment the run count
            context.run.run_count += 1


class SetExpectedStartTime(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:

        # set expected start time if this is the first state
        if not context.run.expected_start_time:
            if context.proposed_state.is_scheduled():
                context.run.expected_start_time = (
                    context.proposed_state.state_details.scheduled_time
                )
            else:
                context.run.expected_start_time = context.proposed_state.timestamp


class SetNextScheduledStartTime(BaseUniversalRule):
    async def before_transition(self, context: OrchestrationContext) -> None:

        # remove the next scheduled start time if exiting a scheduled state
        if context.initial_state and context.initial_state.is_scheduled():
            context.run.next_scheduled_start_time = None

        # set next scheduled start time if entering a scheduled state
        if context.proposed_state.is_scheduled():
            context.run.next_scheduled_start_time = (
                context.proposed_state.state_details.scheduled_time
            )


class UpdateSubflowParentTask(BaseUniversalRule):
    """
    Whenever a subflow changes state, it must update its parent task run's state.
    """

    async def after_transition(self, context: OrchestrationContext) -> None:

        # only applies to flow runs with a parent task run id
        if context.run.parent_task_run_id is not None:

            # avoid mutation of the flow run state
            subflow_parent_task_state = context.validated_state.copy(
                reset_fields=True,
                include={
                    "type",
                    "timestamp",
                    "name",
                    "message",
                    "state_details",
                    "data",
                },
            )

            # set the task's "child flow run id" to be the subflow run id
            subflow_parent_task_state.state_details.child_flow_run_id = context.run.id

            await models.task_runs.set_task_run_state(
                session=context.session,
                task_run_id=context.run.parent_task_run_id,
                state=subflow_parent_task_state,
                force=True,
            )
