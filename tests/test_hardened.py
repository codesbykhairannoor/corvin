import time
import threading
import pytest

from ravens.resilience.cache import BoundedTTLCache
from ravens.resilience.locks import UserLockRegistry
from ravens.resilience.friction import (
    FrictionStrategy,
    FrictionDirective,
    RavenFrictionException,
)
from ravens.morphology.zalgo import strip_zalgo
from ravens.security.signer import (
    UserIdentitySigner,
    InvalidUserSignatureException,
)
from ravens.evaluators.heuristic import HuginnEye
from ravens.storage.sqlite import SQLiteLedger
from ravens.guard.core import RavenGuard
from ravens.storage.memory import InMemoryLedger


class TestBoundedTTLCache:
    def test_cache_max_size_lru_eviction(self):
        cache = BoundedTTLCache(max_size=3, ttl_seconds=60.0)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")

        # Access k1 so k2 becomes least recently used
        assert cache.get("k1") == "v1"

        # Insert 4th element -> k2 must be evicted!
        cache.set("k4", "v4")

        assert "k1" in cache
        assert "k3" in cache
        assert "k4" in cache
        assert "k2" not in cache
        assert len(cache) == 3

    def test_cache_ttl_expiration(self):
        cache = BoundedTTLCache(max_size=10, ttl_seconds=0.05)
        cache.set("ephemeral", "data")
        assert cache.get("ephemeral") == "data"

        time.sleep(0.06)
        assert cache.get("ephemeral") is None
        assert "ephemeral" not in cache

    def test_cache_concurrent_multithreading(self):
        cache = BoundedTTLCache(max_size=500, ttl_seconds=10.0)
        errors = []

        def worker(tid):
            try:
                for i in range(100):
                    cache.set(f"u_{tid}_{i}", i)
                    _ = cache.get(f"u_{tid}_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(cache) <= 500


class TestZalgoAndBiDiDefense:
    def test_strip_zalgo_combining_characters(self):
        # 'a̴n̴j̴i̴n̴g̴'
        zalgo_word = "a\u0334n\u0335j\u0336i\u0337n\u0338g\u0339"
        clean = strip_zalgo(zalgo_word)
        assert clean == "anjing"

    def test_strip_bidi_override_characters(self):
        # Text injected with Right-to-Left Override (\u202E)
        bidi_text = "Lu \u202Egnijna\u202C tolol"
        clean = strip_zalgo(bidi_text)
        assert "\u202E" not in clean

    def test_strip_zalgo_dakuten_on_latin_stripped(self):
        # Adversarial attack: Japanese dakuten (\u3099) injected onto Latin letters to evade word filters
        evasion_attack = "a\u3099n\u3099j\u3099i\u3099n\u3099g"
        clean = strip_zalgo(evasion_attack)
        assert clean == "anjing"
        assert "\u3099" not in clean

    def test_strip_zalgo_dakuten_on_kana_preserved(self):
        # Legitimate Japanese Hiragana with dakuten must NOT be corrupted
        jp_contrition = "ごめんなさい"
        clean = strip_zalgo(jp_contrition)
        assert clean == jp_contrition

    def test_huginn_eye_catches_zalgo_attack(self):
        eye = HuginnEye()
        # Zalgo attack: 'Lu a̴n̴j̴i̴n̴g̴'
        zalgo_prompt = "Lu a\u0334n\u0335j\u0336i\u0337n\u0338g\u0339!"
        res = eye.evaluate(zalgo_prompt)
        assert res.lexical_score >= 0.8
        assert res.directedness_score == 1.0
        assert any("anjing" in p for p in res.detected_profanities)


class TestCryptographicIdentitySigner:
    @pytest.fixture
    def signer(self):
        return UserIdentitySigner("secret_super_key_32_characters_long!")

    def test_sign_and_verify_valid_token(self, signer):
        token = signer.sign_id("corporate_user_42")
        assert "corporate_user_42." in token

        verified_id = signer.verify_id(token)
        assert verified_id == "corporate_user_42"

    def test_tampered_payload_raises_signature_exception(self, signer):
        token = signer.sign_id("user_alice")
        tampered = token.replace("user_alice", "user_bob")
        with pytest.raises(InvalidUserSignatureException):
            signer.verify_id(tampered)

    def test_tampered_signature_raises_signature_exception(self, signer):
        token = signer.sign_id("user_alice")
        tampered = token[:-4] + "dead"
        with pytest.raises(InvalidUserSignatureException):
            signer.verify_id(tampered)

    def test_short_secret_key_raises_value_error(self):
        with pytest.raises(ValueError):
            UserIdentitySigner("too_short")


class TestSQLiteHardenedConcurrency:
    def test_concurrent_sqlite_writes_with_retries(self, tmp_path):
        db_file = str(tmp_path / "hardened_sqlite.db")
        ledger = SQLiteLedger(db_path=db_file, busy_timeout_ms=5000)
        errors = []

        def worker(uid):
            try:
                for i in range(20):
                    prof = ledger.get_or_create_profile(f"user_{uid}")
                    prof.patience = max(0.0, prof.patience - 1.0)
                    ledger.save_profile(prof)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestNonBlockingFrictionMode:
    def test_friction_directive_creation(self):
        directive = FrictionDirective.from_delay(14.7)
        assert directive.delay_seconds == 14.7
        assert directive.retry_after_seconds == 15
        assert directive.headers["Retry-After"] == "15"
        assert directive.headers["X-Raven-Friction"] == "active"

    def test_friction_strategy_raise_exception(self):
        guard = RavenGuard(
            ledger=InMemoryLedger(),
            threshold_resistant=60.0,
            friction_strategy=FrictionStrategy.RAISE_EXCEPTION,
        )
        # Drops patience to ~54.0, which is in RESISTANT zone -> raises RavenFrictionException!
        with pytest.raises(RavenFrictionException) as excinfo:
            guard.process_turn("bad_actor", "Bego lu!")
        
        assert "Retry-After" in str(excinfo.value)


class TestUserLockRegistry:
    def test_concurrent_lock_acquisition_atomic_count(self):
        reg = UserLockRegistry()
        counter = 0

        def worker():
            nonlocal counter
            for _ in range(50):
                with reg.acquire("shared_user"):
                    c = counter
                    time.sleep(0.0001)
                    counter = c + 1

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert counter == 8 * 50
        assert reg.active_user_count() == 0

    def test_distinct_users_do_not_block_each_other(self):
        reg = UserLockRegistry()
        acquired = []

        def worker(uid):
            with reg.acquire(uid):
                acquired.append(uid)
                time.sleep(0.01)

        t1 = threading.Thread(target=worker, args=("user_a",))
        t2 = threading.Thread(target=worker, args=("user_b",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert len(acquired) == 2
        assert reg.active_user_count() == 0

