from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict

class FrictionStrategy(str, Enum):
    """
    Strategy for executing behavioral friction on RESISTANT turns.
    """
    NON_BLOCKING_HEADER = "NON_BLOCKING_HEADER" # Dispatches Retry-After metadata so client/proxy waits, not the server!
    SAFE_SLEEP = "SAFE_SLEEP"                   # Server-side sleep with strict upper clamp
    RAISE_EXCEPTION = "RAISE_EXCEPTION"         # Raises RavenFrictionException immediately


class RavenFrictionException(Exception):
    """
    Raised when a user is in RESISTANT posture and strategy is RAISE_EXCEPTION.
    Client must wait `retry_after_seconds` before re-trying.
    """
    def __init__(self, user_id: str, retry_after_seconds: float, message: str = ""):
        self.user_id = user_id
        self.retry_after_seconds = retry_after_seconds
        default_msg = (
            f"[RavenFriction: user='{user_id}'] Hostility friction active. "
            f"Retry-After: {retry_after_seconds:.1f}s. Slow down."
        )
        super().__init__(message or default_msg)


@dataclass
class FrictionDirective:
    """
    Metadata returned when friction is applied, allowing web frameworks (FastAPI/Flask)
    to return standard HTTP 429 Retry-After headers without blocking server worker threads.
    """
    delay_seconds: float
    retry_after_seconds: int
    headers: Dict[str, str]

    @classmethod
    def from_delay(cls, delay_seconds: float) -> "FrictionDirective":
        retry_int = max(1, int(round(delay_seconds)))
        return cls(
            delay_seconds=delay_seconds,
            retry_after_seconds=retry_int,
            headers={
                "Retry-After": str(retry_int),
                "X-Raven-Friction": "active",
            },
        )

