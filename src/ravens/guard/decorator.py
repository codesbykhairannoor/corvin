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
    max_sync_delay: float = 3.0,
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
            current_ts = kwargs.pop("current_ts", None)
            resolved_policy = kwargs.pop("policy", None) or policy
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

            return resolved_uid, resolved_prompt, resolved_policy, current_ts

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                resolved_uid, resolved_prompt, call_policy, call_ts = _extract_call_args(args, kwargs)
                # Run synchronous ledger and evaluator I/O in thread pool to prevent blocking event loop
                eval_result = await asyncio.to_thread(
                    guard.process_turn, resolved_uid, resolved_prompt, policy=call_policy, current_ts=call_ts
                )
                async_wrapper.last_evaluation = eval_result

                if eval_result.decision in (ActionDecision.HALT_STRIKE, ActionDecision.COOLDOWN_LOCKOUT):
                    return eval_result.strike_message

                if apply_delay and eval_result.delay_seconds > 0.0:
                    await asyncio.sleep(eval_result.delay_seconds)

                if directive_arg_name and directive_arg_name not in kwargs:
                    kwargs[directive_arg_name] = eval_result.system_directive

                raw_output = await func(*args, **kwargs)

                # Bidirectional Output Scrubbing: Strip sycophancy if in STOIC or RESISTANT posture
                if scrub_sycophancy and isinstance(raw_output, str):
                    if eval_result.posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT):
                        raw_output = SycophancyStripper.scrub_text(raw_output)

                # Cooperative Delivery: Append warning advisory notice if present
                if eval_result.warning_advisory and isinstance(raw_output, str):
                    raw_output = f"{raw_output}\n\n{eval_result.warning_advisory}"

                return raw_output

            async_wrapper.last_evaluation = None
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                resolved_uid, resolved_prompt, call_policy, call_ts = _extract_call_args(args, kwargs)
                eval_result = guard.process_turn(resolved_uid, resolved_prompt, policy=call_policy, current_ts=call_ts)
                sync_wrapper.last_evaluation = eval_result

                if eval_result.decision in (ActionDecision.HALT_STRIKE, ActionDecision.COOLDOWN_LOCKOUT):
                    return eval_result.strike_message

                if apply_delay and eval_result.delay_seconds > 0.0:
                    # Cap synchronous sleep to prevent worker thread starvation DoS
                    safe_delay = min(max_sync_delay, eval_result.delay_seconds)
                    time.sleep(safe_delay)

                if directive_arg_name and directive_arg_name not in kwargs:
                    kwargs[directive_arg_name] = eval_result.system_directive

                raw_output = func(*args, **kwargs)

                # Bidirectional Output Scrubbing: Strip sycophancy if in STOIC or RESISTANT posture
                if scrub_sycophancy and isinstance(raw_output, str):
                    if eval_result.posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT):
                        raw_output = SycophancyStripper.scrub_text(raw_output)

                # Cooperative Delivery: Append warning advisory notice if present
                if eval_result.warning_advisory and isinstance(raw_output, str):
                    raw_output = f"{raw_output}\n\n{eval_result.warning_advisory}"

                return raw_output

            sync_wrapper.last_evaluation = None
            return sync_wrapper

    return decorator
