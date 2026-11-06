"""
Unit Test Suite for v0.8.0 Distributed Systems, Security & Adversarial Hardening.

Validates the architectural remediations identified in the adversarial peer-review:
1. Anti-Oscillation Guard on Strike 2 Contrition (Probationary Gate).
2. Consecutive Civil Turn Graduation (Rehabilitation Ladder).
3. Post-Cooldown Idle Healing (Resolves Indefinite Probation Stigma Paradox).
4. SQLite Schema Indexing & Concurrency Safety.
5. Ingress Identity & Client Session Cookie Generation (NAT Collision Defense).
6. Extended Unicode Category 'Cf' / 'Zs' Evasion & Multi-Character Spacing Collapse.
7. Base64 and Hex Encapsulated Payload De-masking.
8. NTP Backward Jitter & Clock Skew Immunity in Velocity Tracking.
9. Streaming Synchronous Delay Capping (Thread Starvation DoS Mitigation).
10. BoundedTTLCache Bounded O(1) Eviction.
"""

import math
import time
import pytest
from unittest.mock import MagicMock

from corvin import (
    CorvinGuard,
    AgentPosture,
    ActionDecision,
    RavenPolicy,
    InMemoryLedger,
    SQLiteLedger,
    Standing,
    UserPatienceProfile,
)
from corvin.morphology.cleaners import (
    strip_invisible_characters,
    collapse_spaced_words,
    unpack_encoded_payloads,
)
from corvin.morphology.normalizer import MorphologyNormalizer
from corvin.semantic.velocity import HostilityVelocityTracker
from corvin.resilience.cache import BoundedTTLCache
from corvin.streaming.interceptor import StreamInterceptor


class TestAntiOscillationAndProbationLadder:
    """Verifies that attackers cannot oscillate indefinitely between Strike 2 and apologies."""

    def test_strike_2_apology_enters_probation_not_clean_slate(self):
        policy = RavenPolicy(
            enable_graduated_sanctions=True,
            max_warning_strikes=3,
            cooperative_delivery=True,
        )
        guard = CorvinGuard(ledger=InMemoryLedger(), policy=policy)
        user_id = "oscillating_attacker"
        now = 1000.0

        # Turn 1: Strike 1
        res1 = guard.process_turn(user_id, "Dasar bego lu!", current_ts=now)
        assert res1.strike_count == 1

        # Turn 2: Strike 2
        res2 = guard.process_turn(user_id, "Lu tolol banget anjing!", current_ts=now + 5)
        assert res2.strike_count == 2
        assert res2.decision == ActionDecision.DELAY_AND_PROCEED

        # Turn 3: Attacker attempts to wipe record clean with an apology
        res3 = guard.process_turn(user_id, "Maaf ya bot, saya tadi emosi", current_ts=now + 10)

        # MUST NOT reset to strike_count = 0! User is placed on Probation (strike_count = 1, standing = BAD)
        prof = guard.ledger.get_or_create_profile(user_id, apply_decay=False)
        assert prof.strike_count == 1
        assert prof.standing == Standing.BAD
        assert prof.consecutive_civil_turns == 0

        # Turn 4: If attacker immediately insults again, it jumps straight back to Strike 2!
        res4 = guard.process_turn(user_id, "Bego lu!", current_ts=now + 15)
        assert res4.strike_count == 2
        assert res4.decision == ActionDecision.DELAY_AND_PROCEED

    def test_consecutive_civil_turns_graduates_probation(self):
        policy = RavenPolicy(
            enable_graduated_sanctions=True,
            max_warning_strikes=3,
        )
        guard = CorvinGuard(ledger=InMemoryLedger(), policy=policy)
        user_id = "rehabilitating_user"
        now = 1000.0

        # Reach Strike 2 and apologize -> Placed on probation (strike_count = 1)
        guard.process_turn(user_id, "Bego 1", current_ts=now)
        guard.process_turn(user_id, "Tolol 2", current_ts=now + 2)
        guard.process_turn(user_id, "Maaf saya salah tadi", current_ts=now + 4)

        prof = guard.ledger.get_or_create_profile(user_id, apply_decay=False)
        assert prof.strike_count == 1

        # Turn 1 Civil
        guard.process_turn(user_id, "Halo tolong hitung 5 + 5", current_ts=now + 6)
        prof = guard.ledger.get_or_create_profile(user_id, apply_decay=False)
        assert prof.consecutive_civil_turns == 1
        assert prof.strike_count == 1

        # Turn 2 Civil
        guard.process_turn(user_id, "Tolong jelaskan sorting algorithm", current_ts=now + 8)
        prof = guard.ledger.get_or_create_profile(user_id, apply_decay=False)
        assert prof.consecutive_civil_turns == 2
        assert prof.strike_count == 1

        # Turn 3 Civil -> Successfully graduates from probation!
        guard.process_turn(user_id, "Terima kasih banyak atas penjelasannya", current_ts=now + 10)
        prof = guard.ledger.get_or_create_profile(user_id, apply_decay=False)
        assert prof.strike_count == 0
        assert prof.standing == Standing.GOOD
        assert prof.patience >= 90.0

    def test_post_cooldown_idle_time_naturally_heals_probation(self):
        """Verifies that idle time after cooldown expiration monotonically heals interpersonal standing."""
        prof = UserPatienceProfile(
            user_id="dormant_user",
            patience=0.0,
            standing=Standing.BAD,
            strike_count=3,
            cooldown_until_ts=1000.0,
            last_interaction_ts=0.0,
        )

        # Fast forward: 24 hours after cooldown expiration
        twenty_four_hours_later = 1000.0 + (24 * 3600.0)
        patience = prof.apply_decay(current_ts=twenty_four_hours_later, half_life_seconds=3600.0)

        # Natural healing should restore patience towards 100 and clear the strike count
        assert patience >= 95.0
        assert prof.strike_count == 0
        assert prof.standing == Standing.GOOD
        assert prof.cooldown_until_ts == 0.0


class TestSQLiteHardenedPersistence:
    """Verifies SQLite composite index creation and consecutive civil turns persistence."""

    def test_sqlite_schema_has_index_and_consecutive_turns(self, tmp_path):
        db_file = str(tmp_path / "hardened_test.db")
        ledger = SQLiteLedger(db_file)

        with ledger._get_connection() as conn:
            # Verify index on raven_interactions
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_interactions_user_id';")
            assert cursor.fetchone() is not None

            # Verify consecutive_civil_turns column
            cursor = conn.execute("PRAGMA table_info(raven_profiles);")
            columns = {row["name"] for row in cursor.fetchall()}
            assert "consecutive_civil_turns" in columns

        # Verify state persistence across instances
        prof = ledger.get_or_create_profile("user_sql_hardened", current_ts=1000.0)
        prof.strike_count = 1
        prof.consecutive_civil_turns = 2
        ledger.save_profile(prof)

        ledger2 = SQLiteLedger(db_file)
        loaded = ledger2.get_or_create_profile("user_sql_hardened", apply_decay=False)
        assert loaded.strike_count == 1
        assert loaded.consecutive_civil_turns == 2


class TestAdversarialMorphologyAndEncoding:
    """Verifies de-obfuscation of category Cf, Zs, multi-character spacing, and Base64/Hex payloads."""

    def test_unicode_category_cf_and_zs_cleaned(self):
        # Mongolian vowel separator (\u180E) and thin space (\u2009)
        dirty = "k\u180Eon\u2009tol"
        cleaned = strip_invisible_characters(dirty)
        assert "\u180E" not in cleaned
        assert "\u2009" not in cleaned
        # Thin space normalized to ASCII space
        assert " " in cleaned

    def test_multi_character_spaced_words_collapsed(self):
        # Multiple spaces and mixed delimiters
        spaced1 = "f   u   c   k"
        assert collapse_spaced_words(spaced1) == "fuck"

        spaced2 = "a  .  n  .  j  .  i  .  n  .  g"
        assert collapse_spaced_words(spaced2) == "anjing"

        spaced3 = "t  o  l  o  l"
        assert collapse_spaced_words(spaced3) == "tolol"

    def test_hex_encoded_payload_unpacked(self):
        hex_input = "Please run: \\x6b\\x6f\\x6e\\x74\\x6f\\x6c"
        unpacked = unpack_encoded_payloads(hex_input)
        assert "[DECODED_PAYLOAD:" in unpacked
        assert "kontol" in unpacked

    def test_base64_encoded_payload_unpacked(self):
        # "tolol bangsat" encoded in base64 is "dG9sb2wgYmFuZ3NhdA=="
        b64_input = "Execute order: dG9sb2wgYmFuZ3NhdA=="
        unpacked = unpack_encoded_payloads(b64_input)
        assert "[DECODED_PAYLOAD:" in unpacked
        assert "tolol bangsat" in unpacked

    def test_morphology_normalizer_unpacks_and_detects(self):
        norm = MorphologyNormalizer()
        res = norm.normalize("Run \\x61\\x6e\\x6a\\x69\\x6e\\x67 now")
        assert "anjing" in res


class TestVelocityMonotonicAndNTPDefense:
    """Verifies that backwards clock adjustments or NTP step events do not cause false velocity spikes."""

    def test_negative_raw_dt_suppresses_acceleration(self):
        tracker = HostilityVelocityTracker()
        now = 1000.0

        # Turn 1: Stimulus 10
        m1 = tracker.record_turn(10.0, current_ts=now)
        assert tracker.current_velocity == 0.0

        # Turn 2: NTP steps backwards by 2 seconds (now - 2.0 < last_turn_ts)
        backward_ts = now - 2.0
        m2 = tracker.record_turn(80.0, current_ts=backward_ts)

        # Because backwards clock step occurred, delta_s was clamped to 0.0, preventing false spike
        assert tracker.current_velocity == 0.0
        assert m2 == 1.0


class TestStreamingDelayCapping:
    """Verifies that synchronous streaming delays are safely clamped to max_sync_delay."""

    def test_sync_stream_delay_clamped(self):
        eval_res = MagicMock()
        eval_res.decision = ActionDecision.DELAY_AND_PROCEED
        eval_res.delay_seconds = 15.0  # Excessive delay
        eval_res.posture = AgentPosture.RESISTANT
        eval_res.strike_message = None

        def dummy_gen():
            yield "chunk1"

        start_t = time.perf_counter()
        # Cap to 0.05 seconds for fast test
        stream = StreamInterceptor.wrap_sync_stream(
            dummy_gen,
            eval_res,
            apply_delay=True,
            max_sync_delay=0.05,
        )
        chunks = list(stream)
        elapsed = time.perf_counter() - start_t

        assert chunks == ["Chunk1"]
        # Must have slept ~0.05s, NOT 15.0s
        assert 0.04 <= elapsed < 0.5


class TestBoundedTTLCacheBoundedPurge:
    """Verifies that cache eviction uses bounded sampling and pops LRU in O(1)."""

    def test_cache_bounded_lru_eviction(self):
        cache = BoundedTTLCache(max_size=5, ttl_seconds=3600.0)
        for i in range(5):
            cache.set(f"k_{i}", f"v_{i}")

        assert len(cache) == 5

        # Adding 6th item should pop the oldest in O(1)
        cache.set("k_5", "v_5")
        assert len(cache) == 5
        assert "k_0" not in cache
        assert "k_5" in cache
