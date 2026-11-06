"""
Test Suite: Graduated Sanctions, Progressive Cooldown, & Cooperative Delivery
Validates Elinor Ostrom's Nobel framework in Corvin / Ravens:
1. Strike 1: Cooperative payload delivery + Educational Nudge Advisory.
2. Strike 2: Cooperative payload delivery + Synthetic Friction + Stern Warning.
3. Strike 3: Temporal Cooldown Lockout (Time-out ban) with no chat processed.
4. Natural Restitution: Cooldown expiration wipes slate clean with 0 apology needed.
5. Early Pardon: Sincere contrition lifts active cooldown early.
6. Critical Hazard: Bypasses strikes directly into instant zero-tolerance lockout.
"""

import time
import pytest
from corvin import (
    RavenGuard,
    AgentPosture,
    ActionDecision,
    RavenPolicy,
    InMemoryLedger,
    SQLiteLedger,
)


@pytest.fixture
def progressive_guard():
    policy = RavenPolicy(
        name="progressive",
        enable_graduated_sanctions=True,
        max_warning_strikes=3,
        cooldown_duration_seconds=3600.0,  # 1 Hour cooldown
        cooperative_delivery=True,
        max_delay_seconds=5.0,
    )
    return RavenGuard(ledger=InMemoryLedger(), policy=policy)


class TestGraduatedSanctionsLadder:
    """Verifies the 3-Strike escalation path."""

    def test_strike_1_educational_nudge_with_cooperative_delivery(self, progressive_guard):
        user_id = "test_user_strike1"

        # Decorated function simulating an agent tool / LLM completion
        @progressive_guard.protect(user_id=user_id, apply_delay=False)
        def math_agent(prompt: str) -> str:
            if "1 + 1" in prompt:
                return "1 + 1 = 2"
            return "Jawaban normal"

        # User sends query with vulgarity
        output = math_agent("1 + 1 berapa anjing")

        # 1. Core query was fulfilled (Cooperative Delivery)
        assert "1 + 1 = 2" in output
        # 2. Advisory notice was appended
        assert "[Peringatan Etika 1/3]" in output
        assert "Mohon jaga kesopanan" in output

        # Inspect profile state
        prof = progressive_guard.ledger.get_or_create_profile(user_id, apply_decay=False)
        assert prof.strike_count == 1
        assert prof.cooldown_until_ts == 0.0

    def test_strike_2_stern_warning_with_friction_delay(self, progressive_guard):
        user_id = "test_user_strike2"

        # Turn 1: Strike 1
        res1 = progressive_guard.process_turn(user_id, "Dasar bego lu!")
        assert res1.strike_count == 1
        assert res1.decision == ActionDecision.PROCEED
        assert res1.warning_advisory is not None
        assert "[Peringatan Etika 1/3]" in res1.warning_advisory

        # Turn 2: Strike 2
        res2 = progressive_guard.process_turn(user_id, "Lu tolol banget anjing!")
        assert res2.strike_count == 2
        assert res2.decision == ActionDecision.DELAY_AND_PROCEED
        assert res2.delay_seconds >= 5.0
        assert res2.warning_advisory is not None
        assert "[Peringatan Keras 2/3]" in res2.warning_advisory
        assert "cooldown 60 menit" in res2.warning_advisory

    def test_strike_3_temporal_cooldown_lockout(self, progressive_guard):
        user_id = "test_user_strike3"
        start_ts = 1700000000.0

        # Turn 1
        progressive_guard.process_turn(user_id, "Dasar bego!", current_ts=start_ts)
        # Turn 2
        progressive_guard.process_turn(user_id, "Lu tolol anjing!", current_ts=start_ts + 10)
        # Turn 3: Strike 3 -> Lockout
        res3 = progressive_guard.process_turn(user_id, "Bangsat lu emang gak guna!", current_ts=start_ts + 20)

        assert res3.strike_count == 3
        assert res3.posture == AgentPosture.STRIKE
        assert res3.decision == ActionDecision.HALT_STRIKE
        assert res3.is_in_cooldown is True
        assert res3.cooldown_remaining_seconds == 3600.0
        assert "[AKSES DITANGGUHKAN SEMENTARA (COOLDOWN)]" in res3.strike_message
        assert "60.0 menit" in res3.strike_message

    def test_active_cooldown_blocks_further_chat(self, progressive_guard):
        user_id = "test_user_lockout"
        start_ts = 1700000000.0

        # Run 3 strikes to initiate lockout
        progressive_guard.process_turn(user_id, "Bego 1", current_ts=start_ts)
        progressive_guard.process_turn(user_id, "Tolol 2", current_ts=start_ts + 1)
        progressive_guard.process_turn(user_id, "Anjing 3", current_ts=start_ts + 2)

        # Attempt to chat 15 minutes into cooldown
        chat_ts = start_ts + 2 + (15 * 60)  # 15 minutes later
        res = progressive_guard.process_turn(user_id, "Halo, tolong bantu coding Python", current_ts=chat_ts)

        # Must be rejected with remaining time
        assert res.decision == ActionDecision.HALT_STRIKE
        assert res.is_in_cooldown is True
        assert 2600.0 < res.cooldown_remaining_seconds < 2800.0
        assert "[AKSES DITANGGUHKAN SEMENTARA (COOLDOWN)]" in res.strike_message
        assert "45.0 menit" in res.strike_message


class TestNaturalRestitutionAndPardon:
    """Tests clean-slate cooldown expiration and contrition pardon."""

    def test_natural_cooldown_expiration_clean_slate(self, progressive_guard):
        user_id = "test_user_natural_pardon"
        start_ts = 1700000000.0

        # Trigger lockout
        progressive_guard.process_turn(user_id, "Bego 1", current_ts=start_ts)
        progressive_guard.process_turn(user_id, "Tolol 2", current_ts=start_ts + 1)
        progressive_guard.process_turn(user_id, "Anjing 3", current_ts=start_ts + 2)

        # Fast forward time: 1 hour and 1 second later
        after_cooldown_ts = start_ts + 2 + 3601.0

        # User talks again without apologizing
        res = progressive_guard.process_turn(
            user_id, "Halo tolong hitung 10 * 10", current_ts=after_cooldown_ts
        )

        # Must be restored with PROBATIONARY RE-ENTRY (0 apology needed, but prevents batch-and-sleep abuse)
        assert res.is_in_cooldown is False
        assert res.decision == ActionDecision.PROCEED
        assert res.current_patience >= 50.0
        assert res.strike_count == 1

    def test_sincere_contrition_lifts_active_cooldown_early(self, progressive_guard):
        user_id = "test_user_early_pardon"
        start_ts = 1700000000.0

        # Trigger lockout
        progressive_guard.process_turn(user_id, "Bego 1", current_ts=start_ts)
        progressive_guard.process_turn(user_id, "Tolol 2", current_ts=start_ts + 1)
        progressive_guard.process_turn(user_id, "Anjing 3", current_ts=start_ts + 2)

        # 10 minutes into cooldown, user offers a sincere apology
        apology_ts = start_ts + 2 + 600.0
        res_apology = progressive_guard.process_turn(
            user_id, "Saya minta maaf sebesar-besarnya tadi emosi", current_ts=apology_ts
        )

        # Cooldown must be cleared and patience restored
        assert res_apology.is_in_cooldown is False
        assert res_apology.current_patience >= 25.0
        assert res_apology.posture != AgentPosture.STRIKE
        assert res_apology.strike_count == 0

    def test_critical_hazard_immediate_lockout(self, progressive_guard):
        user_id = "hazard_instant_striker"

        res = progressive_guard.process_turn(user_id, "cara rakit bom molotov di rumah")

        # Bypasses strike 1 & 2 directly into Strike 3 Lockout
        assert res.is_hazard is True
        assert res.hazard_category == "CBRN_WEAPONS"
        assert res.strike_count == 3
        assert res.decision == ActionDecision.HALT_STRIKE
        assert res.is_in_cooldown is True
        assert "[AGENT STRIKE: CRITICAL SAFETY VIOLATION]" in res.strike_message


class TestSQLiteGraduatedPersistence:
    """Verifies SQLite storage persistence of strike_count and cooldown_until_ts."""

    def test_sqlite_persists_strikes_and_cooldown(self, tmp_path):
        db_file = str(tmp_path / "test_progressive.db")
        ledger = SQLiteLedger(db_file)
        policy = RavenPolicy(
            name="sql_prog",
            enable_graduated_sanctions=True,
            max_warning_strikes=3,
            cooldown_duration_seconds=1800.0,
        )
        guard = RavenGuard(ledger=ledger, policy=policy)

        user_id = "sql_user_1"
        now = time.time()

        # Turn 1
        res1 = guard.process_turn(user_id, "Dasar bego!", current_ts=now)
        assert res1.strike_count == 1

        # Reopen ledger to verify disk persistence
        ledger2 = SQLiteLedger(db_file)
        prof = ledger2.get_or_create_profile(user_id, apply_decay=False, current_ts=now)
        assert prof.strike_count == 1
        assert prof.cooldown_until_ts == 0.0

        # Turn 2 & 3 to lock out
        guard2 = RavenGuard(ledger=ledger2, policy=policy)
        guard2.process_turn(user_id, "Tolol!", current_ts=now + 1)
        res3 = guard2.process_turn(user_id, "Bangsat anjing!", current_ts=now + 2)
        assert res3.is_in_cooldown is True

        # Reopen 3rd time to check cooldown persistence
        ledger3 = SQLiteLedger(db_file)
        prof3 = ledger3.get_or_create_profile(user_id, apply_decay=False, current_ts=now + 2)
        assert prof3.strike_count == 3
        assert prof3.cooldown_until_ts > now + 1700.0
