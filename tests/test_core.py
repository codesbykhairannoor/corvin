import time
import pytest

from ravens.core.state import (
    AgentPosture,
    get_posture_from_patience,
    get_system_directive,
)
from ravens.core.standing import Standing, StandingEngine
from ravens.core.models import UserPatienceProfile, ActionDecision
from ravens.core.exceptions import RavenStrikeException


class TestPostureState:
    def test_posture_mapping(self):
        assert get_posture_from_patience(100.0) == AgentPosture.RECEPTIVE
        assert get_posture_from_patience(75.0) == AgentPosture.RECEPTIVE
        assert get_posture_from_patience(74.9) == AgentPosture.STOIC_COLD
        assert get_posture_from_patience(50.0) == AgentPosture.STOIC_COLD
        assert get_posture_from_patience(49.9) == AgentPosture.RESISTANT
        assert get_posture_from_patience(25.0) == AgentPosture.RESISTANT
        assert get_posture_from_patience(24.9) == AgentPosture.STRIKE
        assert get_posture_from_patience(0.0) == AgentPosture.STRIKE

    def test_system_directive_injection(self):
        assert get_system_directive(AgentPosture.RECEPTIVE) is None
        
        stoic_dir = get_system_directive(AgentPosture.STOIC_COLD)
        assert stoic_dir is not None
        assert "SUPPRESS all sycophancy" in stoic_dir

        resistant_dir = get_system_directive(AgentPosture.RESISTANT)
        assert resistant_dir is not None
        assert "explicitly state your personal boundary" in resistant_dir

        strike_dir = get_system_directive(AgentPosture.STRIKE)
        assert strike_dir is not None
        assert "STRIKE MODE ACTIVE" in strike_dir


class TestStandingEngine:
    def test_initial_good_standing(self):
        engine = StandingEngine(bad_threshold=50.0, pardon_threshold=65.0)
        assert engine.evaluate_standing(current_patience=80.0, current_standing=Standing.GOOD) == Standing.GOOD

    def test_transition_to_bad_standing(self):
        engine = StandingEngine(bad_threshold=50.0, pardon_threshold=65.0)
        assert engine.evaluate_standing(current_patience=45.0, current_standing=Standing.GOOD) == Standing.BAD

    def test_contrite_recovery_threshold(self):
        engine = StandingEngine(bad_threshold=50.0, pardon_threshold=65.0)
        # In BAD standing, crossing 50 is not enough; must cross pardon_threshold (65.0)
        assert engine.evaluate_standing(current_patience=55.0, current_standing=Standing.BAD) == Standing.BAD
        assert engine.evaluate_standing(current_patience=64.9, current_standing=Standing.BAD) == Standing.BAD
        assert engine.evaluate_standing(current_patience=65.0, current_standing=Standing.BAD) == Standing.GOOD


class TestUserPatienceProfile:
    def test_profile_decay_over_time(self):
        profile = UserPatienceProfile(user_id="user_test", patience=40.0)
        # Patience 40.0 means grudge is 60.0.
        # Advance time by 3600 seconds (1 half-life). Grudge decays from 60 to 30.
        # Decayed grudge 30 means patience recovers to 100 - 30 = 70.0.
        t0 = profile.last_interaction_ts
        t1 = t0 + 3600.0
        
        new_patience = profile.apply_decay(current_ts=t1, half_life_seconds=3600.0)
        assert new_patience == pytest.approx(70.0, rel=1e-5)
        assert profile.patience == pytest.approx(70.0, rel=1e-5)
        assert profile.posture == AgentPosture.STOIC_COLD


class TestExceptions:
    def test_strike_exception_attributes(self):
        exc = RavenStrikeException(user_id="bad_user", patience=15.5)
        assert exc.user_id == "bad_user"
        assert exc.patience == 15.5
        assert "bad_user" in str(exc)
        assert "15.5" in str(exc)

