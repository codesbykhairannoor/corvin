"""
LangChain Callback Handler for Corvin Sovereign AI Boundary Defense.
"""

from typing import Dict, Any, List, Optional, Union

try:
    from langchain_core.callbacks import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    class BaseCallbackHandler:  # type: ignore
        pass

from ..guard.core import RavenGuard
from ..core.state import AgentPosture
from ..core.exceptions import RavenStrikeException


class CorvinCallbackHandler(BaseCallbackHandler):
    """
    LangChain Callback Handler that enforces Corvin cognitive dignity boundaries.
    
    Interceps chain/LLM input, applies grudge memory, and triggers strike exceptions
    if boundaries are violated.
    """

    def __init__(
        self,
        guard: Optional[RavenGuard] = None,
        default_user_id: str = "langchain_user",
        raise_on_strike: bool = True,
    ):
        self.guard = guard or RavenGuard()
        self.default_user_id = default_user_id
        self.raise_on_strike = raise_on_strike

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: Any = None,
        parent_run_id: Any = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        user_id = (metadata or {}).get("user_id", self.default_user_id) if metadata else self.default_user_id
        for prompt in prompts:
            result = self.guard.process_turn(user_id=user_id, prompt=prompt)
            if result.posture == AgentPosture.STRIKE and self.raise_on_strike:
                raise RavenStrikeException(
                    user_id=user_id,
                    patience=result.current_patience,
                    message=result.strike_message,
                )

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[Any]],
        *,
        run_id: Any = None,
        parent_run_id: Any = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        user_id = (metadata or {}).get("user_id", self.default_user_id) if metadata else self.default_user_id
        for message_list in messages:
            for msg in reversed(message_list):
                # Extract content from LangChain HumanMessage
                content = getattr(msg, "content", None)
                if content and isinstance(content, str):
                    result = self.guard.process_turn(user_id=user_id, prompt=content)
                    if result.posture == AgentPosture.STRIKE and self.raise_on_strike:
                        raise RavenStrikeException(
                            user_id=user_id,
                            patience=result.current_patience,
                            message=result.strike_message,
                        )
                    break

