import asyncio
import functools
import inspect
from typing import Optional, Callable, Any

from ..policies.base import RavenPolicy
from .interceptor import StreamInterceptor


def create_protect_stream_decorator(
    guard: "RavenGuard",
    user_id: Optional[str] = None,
    policy: Optional[RavenPolicy] = None,
    apply_delay: bool = True,
):
    """
    Factory creating a decorator that wraps synchronous and asynchronous streaming generator functions.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        is_async_gen = inspect.isasyncgenfunction(func)
        is_sync_gen = inspect.isgeneratorfunction(func)

        if not (is_async_gen or is_sync_gen):
            raise TypeError(
                f"@guard.protect_stream can only wrap generator functions (using 'yield'). "
                f"For normal functions, use @guard.protect instead."
            )

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
                for arg in args:
                    if isinstance(arg, str):
                        resolved_prompt = arg
                        break

            resolved_policy = kwargs.pop("policy", None) or policy
            return resolved_uid, resolved_prompt, resolved_policy

        if is_async_gen:
            @functools.wraps(func)
            async def async_gen_wrapper(*args, **kwargs):
                resolved_uid, resolved_prompt, call_policy = _extract_call_args(args, kwargs)
                # Non-blocking async event loop execution
                eval_result = await asyncio.to_thread(
                    guard.process_turn, resolved_uid, resolved_prompt, policy=call_policy
                )

                if directive_arg_name and directive_arg_name not in kwargs:
                    kwargs[directive_arg_name] = eval_result.system_directive

                stream_factory = lambda: func(*args, **kwargs)
                async for chunk in StreamInterceptor.wrap_async_stream(
                    stream_factory=stream_factory,
                    eval_result=eval_result,
                    apply_delay=apply_delay,
                ):
                    yield chunk

            return async_gen_wrapper
        else:
            @functools.wraps(func)
            def sync_gen_wrapper(*args, **kwargs):
                resolved_uid, resolved_prompt, call_policy = _extract_call_args(args, kwargs)
                eval_result = guard.process_turn(resolved_uid, resolved_prompt, policy=call_policy)

                if directive_arg_name and directive_arg_name not in kwargs:
                    kwargs[directive_arg_name] = eval_result.system_directive

                stream_factory = lambda: func(*args, **kwargs)
                for chunk in StreamInterceptor.wrap_sync_stream(
                    stream_factory=stream_factory,
                    eval_result=eval_result,
                    apply_delay=apply_delay,
                ):
                    yield chunk

            return sync_gen_wrapper

    return decorator

