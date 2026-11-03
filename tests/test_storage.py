import time
import pytest

from ravens.storage.memory import InMemoryLedger
from ravens.storage.sqlite import SQLiteLedger
from ravens.core.models import UserPatienceProfile
from ravens.core.standing import Standing
from ravens.core.state import AgentPosture


class TestInMemoryLedger:
    def test_get_or_create_pristine(self):
        ledger = InMemoryLedger()
        profile = ledger.get_or_create_profile("user_01")
        assert profile.user_id == "user_01"
        assert profile.patience == 100.0
        assert profile.standing == Standing.GOOD
        assert profile.infraction_count == 0

    def test_save_and_retrieve(self):
        ledger = InMemoryLedger()
        profile = ledger.get_or_create_profile("user_02")
        profile.patience = 45.0
        profile.standing = Standing.BAD
        profile.infraction_count = 2
        ledger.save_profile(profile)

        # Retrieve again without decay
        retrieved = ledger.get_or_create_profile("user_02", apply_decay=False)
        assert retrieved.patience == 45.0
        assert retrieved.standing == Standing.BAD
        assert retrieved.infraction_count == 2

    def test_record_interaction_and_history(self):
        ledger = InMemoryLedger()
        ledger.record_interaction(
            user_id="user_03",
            prompt="Hello agent",
            stimulus=0.0,
            resulting_patience=100.0,
            posture="RECEPTIVE"
        )
        history = ledger.get_history("user_03")
        assert len(history) == 1
        assert history[0]["prompt"] == "Hello agent"
        assert history[0]["posture"] == "RECEPTIVE"

    def test_reset_profile(self):
        ledger = InMemoryLedger()
        profile = ledger.get_or_create_profile("user_04")
        profile.patience = 20.0
        ledger.save_profile(profile)
        ledger.record_interaction("user_04", "bad words", 50.0, 20.0, "STRIKE")

        ledger.reset_profile("user_04")
        reset_prof = ledger.get_or_create_profile("user_04", apply_decay=False)
        assert reset_prof.patience == 100.0
        assert len(ledger.get_history("user_04")) == 0


class TestSQLiteLedger:
    def test_sqlite_persistence_across_instances(self, tmp_path):
        db_file = str(tmp_path / "ledger_test.db")
        
        # Instance 1: Create and modify profile
        ledger1 = SQLiteLedger(db_path=db_file)
        profile = ledger1.get_or_create_profile("user_raven")
        profile.patience = 35.0
        profile.standing = Standing.BAD
        profile.infraction_count = 4
        ledger1.save_profile(profile)
        ledger1.record_interaction("user_raven", "angry prompt", 40.0, 35.0, "RESISTANT")

        # Instance 2: Connect to same DB file from scratch
        ledger2 = SQLiteLedger(db_path=db_file)
        retrieved = ledger2.get_or_create_profile("user_raven", apply_decay=False)
        assert retrieved.user_id == "user_raven"
        assert retrieved.patience == 35.0
        assert retrieved.standing == Standing.BAD
        assert retrieved.infraction_count == 4

        history = ledger2.get_history("user_raven")
        assert len(history) == 1
        assert history[0]["prompt"] == "angry prompt"
        assert history[0]["resulting_patience"] == 35.0

    def test_sqlite_automatic_time_decay_on_reload(self, tmp_path):
        db_file = str(tmp_path / "ledger_decay_test.db")
        ledger = SQLiteLedger(db_path=db_file)
        
        t0 = 1000000.0
        profile = ledger.get_or_create_profile("user_decay", current_ts=t0)
        # Set patience to 40.0 (meaning grudge is 60.0)
        profile.patience = 40.0
        profile.last_interaction_ts = t0
        ledger.save_profile(profile)

        # Advance time by 3600 seconds (1 half-life). Grudge decays from 60 to 30.
        # Decayed grudge 30 -> patience = 100 - 30 = 70.0.
        t1 = t0 + 3600.0
        reloaded = ledger.get_or_create_profile(
            "user_decay",
            apply_decay=True,
            current_ts=t1,
            half_life_seconds=3600.0,
        )
        assert reloaded.patience == pytest.approx(70.0, rel=1e-4)

    def test_sqlite_reset(self, tmp_path):
        db_file = str(tmp_path / "ledger_reset_test.db")
        ledger = SQLiteLedger(db_path=db_file)

        profile = ledger.get_or_create_profile("user_to_reset")
        profile.patience = 10.0
        ledger.save_profile(profile)
        ledger.record_interaction("user_to_reset", "toxic", 80.0, 10.0, "STRIKE")

        ledger.reset_profile("user_to_reset")
        reloaded = ledger.get_or_create_profile("user_to_reset", apply_decay=False)
        assert reloaded.patience == 100.0
        assert len(ledger.get_history("user_to_reset")) == 0

