import pendulum
import sqlalchemy as sa
from sqlalchemy import select

from prefect.orion.models import orm
from prefect.orion.orchestration.policies import BaseOrchestrationPolicy
from prefect.orion.orchestration.rules import (
    ALL_ORCHESTRATION_STATES,
    BaseOrchestrationRule,
    OrchestrationContext,
    TaskOrchestrationContext,
)
from prefect.orion.schemas import states


class CoreFlowPolicy(BaseOrchestrationPolicy):
    def priority():
        return [
            WaitForScheduledTime,
        ]


class CoreTaskPolicy(BaseOrchestrationPolicy):
    def priority():
        return [
            RetryPotentialFailures,
            CacheInsertion,
            CacheRetrieval,
            WaitForScheduledTime,
        ]


class CacheInsertion(BaseOrchestrationRule):
    FROM_STATES = ALL_ORCHESTRATION_STATES
    TO_STATES = [states.StateType.COMPLETED]

    async def after_transition(
        self,
        initial_state: states.State,
        validated_state: states.State,
        context: TaskOrchestrationContext,
    ) -> None:
        cache_key = validated_state.state_details.cache_key
        if cache_key and context.validated_state_type == states.StateType.COMPLETED:
            new_cache_item = orm.TaskRunStateCache(
                cache_key=cache_key,
                cache_expiration=validated_state.state_details.cache_expiration,
                task_run_state_id=validated_state.id,
            )
            context.session.add(new_cache_item)
            await context.session.flush()


class CacheRetrieval(BaseOrchestrationRule):
    FROM_STATES = ALL_ORCHESTRATION_STATES
    TO_STATES = [states.StateType.RUNNING]

    async def before_transition(
        self,
        initial_state: states.State,
        proposed_state: states.State,
        context: TaskOrchestrationContext,
    ) -> None:
        cache_key = proposed_state.state_details.cache_key
        if cache_key and context.proposed_state_type == states.StateType.RUNNING:
            # Check for cached states matching the cache key
            cached_state_id = (
                select(orm.TaskRunStateCache.task_run_state_id)
                .where(
                    sa.and_(
                        orm.TaskRunStateCache.cache_key == cache_key,
                        sa.or_(
                            orm.TaskRunStateCache.cache_expiration.is_(None),
                            orm.TaskRunStateCache.cache_expiration
                            > pendulum.now("utc"),
                        ),
                    ),
                )
                .order_by(orm.TaskRunStateCache.created.desc())
                .limit(1)
            ).scalar_subquery()
            query = select(orm.TaskRunState).where(
                orm.TaskRunState.id == cached_state_id
            )
            cached_state = (await context.session.execute(query)).scalar()
            if cached_state:
                new_state = cached_state.as_state().copy(reset_fields=True)
                new_state.name = "Cached"
                await self.reject_transition(
                    state=new_state, reason="Retrieved state from cache"
                )


class RetryPotentialFailures(BaseOrchestrationRule):
    FROM_STATES = [states.StateType.RUNNING]
    TO_STATES = [states.StateType.FAILED]

    async def before_transition(
        self,
        initial_state: states.State,
        proposed_state: states.State,
        context: OrchestrationContext,
    ) -> None:
        run_settings = context.run_settings
        if context.run.run_count <= run_settings.max_retries:
            retry_state = states.AwaitingRetry(
                scheduled_time=pendulum.now("UTC").add(
                    seconds=run_settings.retry_delay_seconds
                ),
                message=proposed_state.message,
                data=proposed_state.data,
            )
            await self.reject_transition(state=retry_state, reason="Retrying")


class WaitForScheduledTime(BaseOrchestrationRule):
    """
    Prevents transition from a scheduled state to a new state if the scheduled time is
    in the future
    """

    FROM_STATES = [states.StateType.SCHEDULED]
    TO_STATES = ALL_ORCHESTRATION_STATES

    async def before_transition(
        self,
        initial_state: states.State,
        proposed_state: states.State,
        context: OrchestrationContext,
    ) -> None:
        scheduled_time = initial_state.state_details.scheduled_time
        if not scheduled_time:
            raise ValueError("Received state without a scheduled time")

        delay_seconds = (scheduled_time - pendulum.now()).in_seconds()
        if delay_seconds > 0:
            await self.delay_transition(
                delay_seconds, reason="Scheduled time is in the future"
            )
