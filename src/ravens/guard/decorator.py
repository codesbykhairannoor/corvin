import asyncio
import functools
import inspect
import time
from typing import Optional, Callable, Any

from ..core.models import ActionDecision
from ..core.state import AgentPosture
from ..policies.base import RavenPolicy
from ..scrubbers.stripper import SycophancyStripper

def create_protect_decorator(
    guard: "RavenGuard",
    user_id: Optional[str] = None,
    policy: Optional[RavenPolicy] = None,
    apply_delay: bool = True,
    scrub_sycophancy: bool = True,
):
    """
    Factory creating a decorator that wraps sync or async agent functions with an active policy
    and bidirectional sycophancy output scrubbing.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        is_async = inspect.iscoroutinefunction(func)

        directive_arg_name = None
        for candidate in ("directive", "system_directive", "raven_directive"):
            if candidate in param_names:
                directive_arg_name = candidate
                break

        def _extract_call_args(args, kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound_args = bound.arguments

            resolved_uid = user_id
            if resolved_uid is None:
                if "user_id" in bound_args:
                    resolved_uid = str(bound_args["user_id"])
                elif "auth_token" in bound_args:
                    resolved_uid = str(bound_args["auth_token"])
                elif "user_id" in kwargs:
                    resolved_uid = str(kwargs["user_id"])
                else:
                    resolved_uid = "anonymous"

            resolved_prompt = ""
            for prompt_candidate in ("prompt", "message", "text", "query", "user_input"):
                if prompt_candidate in bound_args:
                    resolved_prompt = str(bound_args[prompt_candidate])
                    break

            if not resolved_prompt:
                # If not found in bound args, inspect positional args skipping 'self' / 'cls'
                for arg in args:
                    if isinstance(arg, str):
                        resolved_prompt = arg
                        break

            resolved_policy = kwargs.pop("policy", None) or policy
            return resolved_uid, resolved_prompt, resolved_policy

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                resolved_uid, resolved_prompt, call_policy = _extract_call_args(args, kwargs)
                # Run synchronous ledger and evaluator I/O in thread pool to prevent blocking event loop
                eval_result = await asyncio.to_thread(
                    guard.process_turn, resolved_uid, resolved_prompt, policy=call_policy
                )

                if eval_result.decision == ActionDecision.HALT_STRIKE:
                    return eval_result.strike_message

                if apply_delay and eval_result.delay_seconds > 0.0:
                    await asyncio.sleep(eval_result.delay_seconds)

                if directive_arg_name and directive_arg_name not in kwargs:
                    kwargs[directive_arg_name] = eval_result.system_directive

                raw_output = await func(*args, **kwargs)

                # Bidirectional Output Scrubbing: Strip sycophancy if in STOIC or RESISTANT posture
                if scrub_sycophancy and isinstance(raw_output, str):
                    if eval_result.posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT):
                        return SycophancyStripper.scrub_text(raw_output)

                return raw_output

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                resolved_uid, resolved_prompt, call_policy = _extract_call_args(args, kwargs)
                eval_result = guard.process_turn(resolved_uid, resolved_prompt, policy=call_policy)

                if eval_result.decision == ActionDecision.HALT_STRIKE:
                    return eval_result.strike_message

                if apply_delay and eval_result.delay_seconds > 0.0:
                    time.sleep(eval_result.delay_seconds)

                if directive_arg_name and directive_arg_name not in kwargs:
                    kwargs[directive_arg_name] = eval_result.system_directive

                raw_output = func(*args, **kwargs)

                # Bidirectional Output Scrubbing: Strip sycophancy if in STOIC or RESISTANT posture
                if scrub_sycophancy and isinstance(raw_output, str):
                    if eval_result.posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT):
                        return SycophancyStripper.scrub_text(raw_output)

                return raw_output

            return sync_wrapper

    return decorator
