import contextlib
import pendulum
import pytest

from prefect.orion.schemas.responses import SetStateStatus
from prefect.orion.orchestration.core_policy import (
    WaitForScheduledTime,
    RetryPotentialFailures,
    CacheInsertion,
    CacheRetrieval,
)
from prefect.orion.orchestration.global_policy import (
    UpdateRunDetails,
)
from prefect.orion.schemas import states


@pytest.mark.parametrize("run_type", ["task", "flow"])
class TestWaitForScheduledTimeRule:
    async def test_late_scheduled_states_just_run(
        self,
        session,
        run_type,
        initialize_orchestration,
    ):
        initial_state_type = states.StateType.SCHEDULED
        proposed_state_type = states.StateType.RUNNING
        intended_transition = (initial_state_type, proposed_state_type)
        ctx = await initialize_orchestration(
            session,
            run_type,
            *intended_transition,
            initial_details={"scheduled_time": pendulum.now().subtract(minutes=5)},
        )

        async with WaitForScheduledTime(ctx, *intended_transition) as ctx:
            await ctx.validate_proposed_state()

        assert ctx.validated_state_type == proposed_state_type

    async def test_early_scheduled_states_are_delayed(
        self,
        session,
        run_type,
        initialize_orchestration,
    ):
        initial_state_type = states.StateType.SCHEDULED
        proposed_state_type = states.StateType.RUNNING
        intended_transition = (initial_state_type, proposed_state_type)
        ctx = await initialize_orchestration(
            session,
            run_type,
            *intended_transition,
            initial_details={"scheduled_time": pendulum.now().add(minutes=5)},
        )

        async with WaitForScheduledTime(ctx, *intended_transition) as ctx:
            await ctx.validate_proposed_state()

        assert ctx.response_status == SetStateStatus.WAIT
        assert ctx.proposed_state is None
        assert abs(ctx.response_details.delay_seconds - 300) < 2

    async def test_scheduling_rule_does_not_fire_against_other_state_types(
        self,
        session,
        run_type,
        initialize_orchestration,
    ):
        initial_state_type = states.StateType.PENDING
        proposed_state_type = states.StateType.RUNNING
        intended_transition = (initial_state_type, proposed_state_type)
        ctx = await initialize_orchestration(
            session,
            run_type,
            *intended_transition,
        )

        scheduling_rule = WaitForScheduledTime(ctx, *intended_transition)
        async with scheduling_rule as ctx:
            pass
        assert await scheduling_rule.invalid()


class TestCachingBackendLogic:
    @pytest.mark.parametrize(
        ["expiration", "expected_status", "expected_name"],
        [
            (pendulum.now().subtract(days=1), SetStateStatus.ACCEPT, "Running"),
            (pendulum.now().add(days=1), SetStateStatus.REJECT, "Cached"),
            (None, SetStateStatus.REJECT, "Cached"),
        ],
        ids=["past", "future", "null"],
    )
    async def test_set_and_retrieve_unexpired_cached_states(
        self,
        session,
        initialize_orchestration,
        expiration,
        expected_status,
        expected_name,
    ):
        caching_policy = [CacheInsertion, CacheRetrieval]

        # this first proposed state is added to the cache table
        initial_state_type = states.StateType.RUNNING
        proposed_state_type = states.StateType.COMPLETED
        intended_transition = (initial_state_type, proposed_state_type)
        ctx1 = await initialize_orchestration(
            session,
            "task",
            *intended_transition,
            initial_details={"cache_key": "cache-hit", "cache_expiration": expiration},
            proposed_details={"cache_key": "cache-hit", "cache_expiration": expiration},
        )

        async with contextlib.AsyncExitStack() as stack:
            for rule in caching_policy:
                ctx1 = await stack.enter_async_context(rule(ctx1, *intended_transition))
            await ctx1.validate_proposed_state()

        assert ctx1.response_status == SetStateStatus.ACCEPT

        initial_state_type = states.StateType.PENDING
        proposed_state_type = states.StateType.RUNNING
        intended_transition = (initial_state_type, proposed_state_type)
        ctx2 = await initialize_orchestration(
            session,
            "task",
            *intended_transition,
            initial_details={"cache_key": "cache-hit", "cache_expiration": expiration},
            proposed_details={"cache_key": "cache-hit", "cache_expiration": expiration},
        )

        async with contextlib.AsyncExitStack() as stack:
            for rule in caching_policy:
                ctx2 = await stack.enter_async_context(rule(ctx2, *intended_transition))
            await ctx2.validate_proposed_state()

        assert ctx2.response_status == expected_status
        assert ctx2.validated_state.name == expected_name

    @pytest.mark.parametrize(
        "proposed_state_type",
        set(states.StateType) - set([states.StateType.COMPLETED]),
        ids=lambda statetype: statetype.name,
    )
    async def test_only_cache_completed_states(
        self,
        session,
        initialize_orchestration,
        proposed_state_type,
    ):
        caching_policy = [CacheInsertion, CacheRetrieval]

        # this first proposed state is added to the cache table
        initial_state_type = states.StateType.RUNNING
        intended_transition = (initial_state_type, proposed_state_type)
        ctx1 = await initialize_orchestration(
            session,
            "task",
            *intended_transition,
            initial_details={"cache_key": "cache-hit"},
            proposed_details={"cache_key": "cache-hit"},
        )

        async with contextlib.AsyncExitStack() as stack:
            for rule in caching_policy:
                ctx1 = await stack.enter_async_context(rule(ctx1, *intended_transition))
            await ctx1.validate_proposed_state()

        assert ctx1.response_status == SetStateStatus.ACCEPT

        initial_state_type = states.StateType.PENDING
        proposed_state_type = states.StateType.RUNNING
        intended_transition = (initial_state_type, proposed_state_type)
        ctx2 = await initialize_orchestration(
            session,
            "task",
            *intended_transition,
            initial_details={"cache_key": "cache-hit"},
            proposed_details={"cache_key": "cache-hit"},
        )

        async with contextlib.AsyncExitStack() as stack:
            for rule in caching_policy:
                ctx2 = await stack.enter_async_context(rule(ctx2, *intended_transition))
            await ctx2.validate_proposed_state()

        assert ctx2.response_status == SetStateStatus.ACCEPT


class TestRetryingRule:
    async def test_retry_potential_failures(
        self,
        session,
        initialize_orchestration,
    ):
        retry_policy = [RetryPotentialFailures, UpdateRunDetails]
        initial_state_type = states.StateType.RUNNING
        proposed_state_type = states.StateType.FAILED
        intended_transition = (initial_state_type, proposed_state_type)
        ctx = await initialize_orchestration(
            session,
            "task",
            *intended_transition,
        )

        ctx.run_settings.max_retries = 2
        ctx.run.run_count = 2

        async with contextlib.AsyncExitStack() as stack:
            for rule in retry_policy:
                ctx = await stack.enter_async_context(rule(ctx, *intended_transition))
            await ctx.validate_proposed_state()

        assert ctx.response_status == SetStateStatus.REJECT
        assert ctx.validated_state_type == states.StateType.SCHEDULED

    async def test_stops_retrying_eventually(
        self,
        session,
        initialize_orchestration,
    ):
        retry_policy = [RetryPotentialFailures, UpdateRunDetails]
        initial_state_type = states.StateType.RUNNING
        proposed_state_type = states.StateType.FAILED
        intended_transition = (initial_state_type, proposed_state_type)
        ctx = await initialize_orchestration(
            session,
            "task",
            *intended_transition,
        )

        ctx.run_settings.max_retries = 2
        ctx.run.run_count = 3

        async with contextlib.AsyncExitStack() as stack:
            for rule in retry_policy:
                ctx = await stack.enter_async_context(rule(ctx, *intended_transition))
            await ctx.validate_proposed_state()

        assert ctx.response_status == SetStateStatus.ACCEPT
        assert ctx.validated_state_type == states.StateType.FAILED
