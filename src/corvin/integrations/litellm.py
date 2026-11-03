"""
LiteLLM, OpenAI, and Generic LLM Gateway Interceptor for Corvin Sovereign AI Defense.
"""

from typing import List, Dict, Any, Optional, Callable, Union, Tuple

from ..guard.core import RavenGuard
from ..core.state import AgentPosture
from ..core.models import EvaluationResult
from ..core.exceptions import RavenStrikeException
from ..scrubbers.stripper import SycophancyStripper


class CorvinLLMInterceptor:
    """
    Drop-in interceptor for LiteLLM, OpenAI, Anthropic, and generic LLM clients.
    
    Provides:
    1. Pre-turn boundary check: evaluates user turn, aborts immediately on Strike.
    2. Dynamic Context Injection: injects affective system directives into LLM system prompts.
    3. Post-turn sycophancy stripping: purges servile fawning and bootlicking from model output.
    """

    def __init__(
        self,
        guard: Optional[RavenGuard] = None,
        scrubber: Optional[SycophancyStripper] = None,
        auto_strip_sycophancy: bool = True,
        system_role: str = "system",
    ):
        self.guard = guard or RavenGuard()
        self.scrubber = scrubber or SycophancyStripper()
        self.auto_strip_sycophancy = auto_strip_sycophancy
        self.system_role = system_role

    def extract_latest_user_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """
        Extracts the most recent user turn from an OpenAI-compatible messages array.
        """
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Multi-part content
                    parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                    return " ".join(parts)
        return ""

    def prepare_messages(
        self,
        messages: List[Dict[str, Any]],
        user_id: str = "default_user",
        raise_on_strike: bool = True,
    ) -> Tuple[List[Dict[str, Any]], EvaluationResult]:
        """
        Evaluates the user's latest prompt, verifies boundaries, and injects
        the corresponding posture system directive into the system prompt.
        
        Returns:
            (guarded_messages, evaluation_result)
        """
        prompt = self.extract_latest_user_prompt(messages)
        result = self.guard.process_turn(user_id=user_id, prompt=prompt)

        if result.posture == AgentPosture.STRIKE and raise_on_strike:
            raise RavenStrikeException(
                user_id=user_id,
                patience=result.current_patience,
                message=result.strike_message,
            )

        # Clone messages to avoid mutating caller's original list
        new_messages = [dict(m) for m in messages]

        if result.system_directive:
            # Find existing system message or prepend a new one
            has_system = False
            for m in new_messages:
                if m.get("role") == self.system_role:
                    original_content = m.get("content", "")
                    m["content"] = f"{original_content}\n\n{result.system_directive}".strip()
                    has_system = True
                    break

            if not has_system:
                new_messages.insert(0, {
                    "role": self.system_role,
                    "content": result.system_directive,
                })

        return new_messages, result

    def process_response(self, text: str) -> str:
        """
        Scrubs fawning sycophancy, apologies, and servile openers from LLM response.
        """
        if self.auto_strip_sycophancy:
            return self.scrubber.scrub_text(text)
        return text

    def wrap_completion(
        self,
        completion_callable: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Executes a guarded LLM completion call.
        
        Extracts user_id from kwargs['user'] or defaults to 'anonymous_user'.
        Guards input, executes completion, and strips sycophancy from response.
        """
        messages = kwargs.get("messages", [])
        user_id = kwargs.get("user") or kwargs.get("user_id") or "anonymous_user"

        guarded_messages, result = self.prepare_messages(messages, user_id=user_id)
        kwargs["messages"] = guarded_messages

        # Execute underlying LLM completion
        response = completion_callable(*args, **kwargs)

        # If standard OpenAI/LiteLLM response object with choices
        if hasattr(response, "choices") and response.choices:
            first_choice = response.choices[0]
            if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
                if first_choice.message.content:
                    first_choice.message.content = self.process_response(first_choice.message.content)

        return response
