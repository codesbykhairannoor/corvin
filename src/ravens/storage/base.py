from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from ..core.models import UserPatienceProfile

class BaseLedger(ABC):
    """
    Abstract interface for The Ledger of Muninn (Grudge & Patience Storage).
    """

    @abstractmethod
    def get_or_create_profile(
        self,
        user_id: str,
        apply_decay: bool = True,
        current_ts: Optional[float] = None,
        half_life_seconds: float = 3600.0,
    ) -> UserPatienceProfile:
        """
        Retrieves a user profile by ID, creating a fresh one (Patience = 100) if not found.
        If apply_decay is True, calculates elapsed time and decays the grudge.
        """
        pass

    @abstractmethod
    def save_profile(self, profile: UserPatienceProfile) -> None:
        """
        Persists or updates the user patience profile.
        """
        pass

    @abstractmethod
    def record_interaction(
        self,
        user_id: str,
        prompt: str,
        stimulus: float,
        resulting_patience: float,
        posture: str,
        timestamp: Optional[float] = None,
    ) -> None:
        """
        Appends an interaction event to the user's historical audit ledger.
        """
        pass

    @abstractmethod
    def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves recent interaction events for the given user.
        """
        pass

    @abstractmethod
    def reset_profile(self, user_id: str) -> None:
        """
        Wipes all grudges and resets a user profile to pristine state (Patience = 100).
        """
        pass

