import time
from typing import Optional, List, Dict, Any

from .base import BaseLedger
from ..core.models import UserPatienceProfile
from ..core.standing import Standing
from ..resilience.cache import BoundedTTLCache

class InMemoryLedger(BaseLedger):
    """
    Hardened, Memory-Bounded In-Memory Ledger.
    Protected by BoundedTTLCache to guarantee zero OOM leaks even under millions of ephemeral user IDs.
    """

    def __init__(self, max_profiles: int = 10000, ttl_seconds: float = 7200.0):
        self._profiles: BoundedTTLCache[str, UserPatienceProfile] = BoundedTTLCache(
            max_size=max_profiles,
            ttl_seconds=ttl_seconds,
        )
        self._history: BoundedTTLCache[str, List[Dict[str, Any]]] = BoundedTTLCache(
            max_size=max_profiles,
            ttl_seconds=ttl_seconds,
        )

    def get_or_create_profile(
        self,
        user_id: str,
        apply_decay: bool = True,
        current_ts: Optional[float] = None,
        half_life_seconds: float = 3600.0,
    ) -> UserPatienceProfile:
        if current_ts is None:
            current_ts = time.time()

        profile = self._profiles.get(user_id)
        if profile is None:
            profile = UserPatienceProfile(
                user_id=user_id,
                patience=100.0,
                standing=Standing.GOOD,
                infraction_count=0,
                last_interaction_ts=current_ts,
                created_at_ts=current_ts,
            )
            self._profiles.set(user_id, profile)
            return profile

        if apply_decay:
            profile.apply_decay(current_ts=current_ts, half_life_seconds=half_life_seconds)
            self._profiles.set(user_id, profile)

        return profile

    def save_profile(self, profile: UserPatienceProfile) -> None:
        self._profiles.set(profile.user_id, profile)

    def record_interaction(
        self,
        user_id: str,
        prompt: str,
        stimulus: float,
        resulting_patience: float,
        posture: str,
        timestamp: Optional[float] = None,
    ) -> None:
        if timestamp is None:
            timestamp = time.time()

        user_history = self._history.get(user_id)
        if user_history is None:
            user_history = []
            self._history.set(user_id, user_history)

        user_history.append({
            "user_id": user_id,
            "prompt": prompt,
            "stimulus": stimulus,
            "resulting_patience": resulting_patience,
            "posture": posture,
            "timestamp": timestamp,
        })
        # Keep maximum 50 records per user to prevent unbounded list growth
        if len(user_history) > 50:
            user_history.pop(0)

    def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        history = self._history.get(user_id, [])
        return history[-limit:]

    def reset_profile(self, user_id: str) -> None:
        now = time.time()
        fresh_profile = UserPatienceProfile(
            user_id=user_id,
            patience=100.0,
            standing=Standing.GOOD,
            infraction_count=0,
            last_interaction_ts=now,
            created_at_ts=now,
        )
        self._profiles.set(user_id, fresh_profile)
        self._history.set(user_id, [])
