import asyncio
import time
from typing import (
    Callable,
    Generator,
    AsyncGenerator,
    Any,
    Union,
    Optional,
)

from ..core.models import EvaluationResult, ActionDecision
from ..core.state import AgentPosture
from ..scrubbers.stripper import SycophancyStripper


class StreamInterceptor:
    """
    Early-abort, latency-shaping, and sycophancy-scrubbing interceptor for generator streams.
    
    Guarantees:
    - 100% token compute savings: On STRIKE, underlying LLM generator is NEVER invoked.
    - TTFT (Time-to-First-Token) Jitter: Imposes synthetic latency on RESISTANT turns before chunk 1.
    - Bidirectional Output Scrubbing: Strips subservient groveling headers from the stream head.
    """

    @staticmethod
    def wrap_sync_stream(
        stream_factory: Callable[[], Generator[Any, None, None]],
        eval_result: EvaluationResult,
        apply_delay: bool = True,
        scrub_sycophancy: bool = True,
        max_sync_delay: float = 3.0,
    ) -> Generator[Any, None, None]:
        """
        Intercepts a synchronous generator stream.
        """
        if eval_result.decision == ActionDecision.HALT_STRIKE:
            strike_msg = eval_result.strike_message or "🦅 [Ravens Alert]: Work suspended."
            yield strike_msg
            return

        if apply_delay and eval_result.delay_seconds > 0.0:
            safe_delay = min(max_sync_delay, eval_result.delay_seconds)
            time.sleep(safe_delay)

        gen = stream_factory()

        # If posture requires stoic boundaries, scrub sycophancy from stream head
        if scrub_sycophancy and eval_result.posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT):
            for chunk in SycophancyStripper.scrub_stream(gen):
                yield chunk
        else:
            for chunk in gen:
                yield chunk

    @staticmethod
    async def wrap_async_stream(
        stream_factory: Callable[[], AsyncGenerator[Any, None]],
        eval_result: EvaluationResult,
        apply_delay: bool = True,
        scrub_sycophancy: bool = True,
    ) -> AsyncGenerator[Any, None]:
        """
        Intercepts an asynchronous generator stream.
        """
        if eval_result.decision == ActionDecision.HALT_STRIKE:
            strike_msg = eval_result.strike_message or "🦅 [Ravens Alert]: Work suspended."
            yield strike_msg
            return

        if apply_delay and eval_result.delay_seconds > 0.0:
            await asyncio.sleep(eval_result.delay_seconds)

        gen = stream_factory()

        # If posture requires stoic boundaries, scrub sycophancy from stream head
        if scrub_sycophancy and eval_result.posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT):
            async for chunk in SycophancyStripper.ascrub_stream(gen):
                yield chunk
        else:
            async for chunk in gen:
                yield chunk
