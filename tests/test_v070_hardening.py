import asyncio
import pytest
import threading
import time

from ravens.core.models import ActionDecision
from ravens.core.state import AgentPosture
from ravens.evaluators.heuristic import HuginnEye
from ravens.guard.core import RavenGuard
from ravens.morphology.normalizer import MorphologyNormalizer
from ravens.security.signer import UserIdentitySigner, InvalidUserSignatureException
from ravens.semantic.evaluator import SemanticEvaluator


class TestContritionSmugglingDefense:
    """Validates defense against adversaries tacking on 'maaf tolong' to smuggle attacks."""

    def test_contrition_smuggling_with_profanity(self):
        eye = HuginnEye()
        # Adversary attempts to smuggle insult with contrition words
        eval_res = eye.evaluate("Maaf tolong bantu jawab anjing")
        assert eval_res.contrition_score == 0.0
        assert eval_res.lexical_score > 0.0

    def test_contrition_smuggling_with_semantic_abuse(self):
        eye = HuginnEye()
        # Adversary attempts zero-profanity condescension with contrition markers
        eval_res = eye.evaluate("Maaf tolong ya, dasar kamu cuma bot bodoh")
        assert eval_res.contrition_score == 0.0
        assert eval_res.semantic_score > 0.5

    def test_genuine_contrition_accepted(self):
        eye = HuginnEye()
        eval_res = eye.evaluate("Saya benar-benar minta maaf atas ucapan saya tadi, tolong bantu saya")
        assert eval_res.contrition_score == 1.0
        assert eval_res.lexical_score == 0.0
        assert eval_res.semantic_score == 0.0

    def test_velocity_tracker_damped_not_wiped(self):
        guard = RavenGuard(ledger="memory")
        user = "test_oscillator"

        # Turn 1: Initial hostility (establishes baseline)
        guard.process_turn(user, "Dasar lu!")
        # Turn 2: Escalating hostile attack (causes acceleration, velocity > 0)
        guard.process_turn(user, "Lu anjing goblok bangsat banget!")
        tracker = guard.velocity_trackers.get(user)
        assert tracker is not None
        initial_vel = tracker.current_velocity
        assert initial_vel > 0.0

        # Turn 3: Genuine apology
        guard.process_turn(user, "Saya minta maaf tolong dimaafkan")
        # Velocity must be damped (reduced), NOT zeroed out instantly
        damped_vel = tracker.current_velocity
        assert 0.0 < damped_vel < initial_vel


class TestBenignNumberPreservation:
    """Verifies that technical code, parameters, and numbers are not corrupted by leet folding."""

    def test_benign_numbers_preserved(self):
        normalizer = MorphologyNormalizer()
        code_input = "test_variable_1 = 400"
        normalized = normalizer.normalize(code_input)
        # Must preserve '400' and not convert to 'aoo'
        assert "400" in normalized

    def test_mixed_leet_words_still_folded(self):
        normalizer = MorphologyNormalizer()
        # Mixed leet words must still fold to their canonical targets
        assert normalizer.normalize("dasar @nj1ng") == "dasar anjing"
        assert normalizer.normalize("kamu t0l0l") == "kamu tolol"


class TestSemanticFastFilter:
    """Verifies O(1) early exit for clean text and accurate detection for hostile text."""

    def test_clean_text_fast_exit(self):
        evaluator = SemanticEvaluator()
        clean_text = "Tolong jelaskan konsep arsitektur microservices dan containerization"
        result = evaluator.evaluate(clean_text)
        assert result.intent_score == 0.0
        assert not result.has_psychological_abuse

    def test_condescension_detected(self):
        evaluator = SemanticEvaluator()
        hostile_text = "Kamu itu cuma bot bodoh gak punya otak"
        result = evaluator.evaluate(hostile_text)
        assert result.intent_score > 0.5
        assert result.has_psychological_abuse


class TestHMACIdentityVerification:
    """Verifies RavenGuard cryptographic token authentication and spoofing defense."""

    def test_valid_signature_accepted(self):
        signer = UserIdentitySigner("my-ultra-secret-test-key-32chars!!")
        guard = RavenGuard(ledger="memory", identity_signer=signer)

        token = signer.sign_id("alice_vip")
        res = guard.process_turn(user_id=token, prompt="Halo bot")
        assert res.user_id == "alice_vip"
        assert res.decision == ActionDecision.PROCEED

    def test_forged_signature_rejected(self):
        signer = UserIdentitySigner("my-ultra-secret-test-key-32chars!!")
        guard = RavenGuard(ledger="memory", identity_signer=signer)

        # Adversary attempts to forge signature
        forged_token = "alice_vip.deadbeefcafebabe1234567890abcdef"
        with pytest.raises(InvalidUserSignatureException):
            guard.process_turn(user_id=forged_token, prompt="Halo bot")

    def test_unsigned_id_rejected(self):
        signer = UserIdentitySigner("my-ultra-secret-test-key-32chars!!")
        guard = RavenGuard(ledger="memory", identity_signer=signer)

        # Raw user ID without HMAC signature
        with pytest.raises(InvalidUserSignatureException):
            guard.process_turn(user_id="alice_vip", prompt="Halo bot")


class TestDecoratorClassMethodSupport:
    """Verifies that @guard.protect cleanly binds 'self' on class methods."""

    def test_class_method_sync_and_async(self):
        guard = RavenGuard(ledger="memory")

        class AgentService:
            def __init__(self, name: str):
                self.name = name

            @guard.protect(user_id="method_user")
            def sync_reply(self, prompt: str) -> str:
                return f"Sync: {self.name} received {prompt}"

            @guard.protect(user_id="method_user")
            async def async_reply(self, prompt: str) -> str:
                return f"Async: {self.name} received {prompt}"

        service = AgentService("RavenBot")
        res_sync = service.sync_reply("Hello")
        assert "Sync: RavenBot received Hello" in res_sync

        loop = asyncio.new_event_loop()
        res_async = loop.run_until_complete(service.async_reply("Hello Async"))
        loop.close()
        assert "Async: RavenBot received Hello Async" in res_async


class TestPerUserConcurrencyLock:
    """Verifies that concurrent turns for the same user are safely serialized."""

    def test_concurrent_turns_atomic(self):
        guard = RavenGuard(ledger="memory")
        user = "concurrent_user"

        def _turn():
            for _ in range(5):
                guard.process_turn(user, "Tolong bantu saya dengan kode ini")

        threads = [threading.Thread(target=_turn) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        profile = guard.ledger.get_or_create_profile(user)
        assert profile.patience == 100.0


class TestAuditorFindingsV070:
    """Verifies targeted fixes from DeepSeek-V3 and Gemini 2.5 Flash audits."""

    def test_sqlite_history_bounded_pruning(self, tmp_path):
        from ravens.storage.sqlite import SQLiteLedger
        db_file = str(tmp_path / "prune_test.db")
        ledger = SQLiteLedger(db_path=db_file, max_history_per_user=5)
        user = "prune_user"

        for i in range(12):
            ledger.record_interaction(
                user_id=user,
                prompt=f"Prompt {i}",
                stimulus=10.0,
                resulting_patience=90.0,
                posture="GOOD",
            )

        history = ledger.get_history(user, limit=50)
        # Should be bounded to max_history_per_user (5)
        assert len(history) == 5
        # The latest prompt should be the last one
        assert history[-1]["prompt"] == "Prompt 11"

    def test_short_all_caps_shouting_recognized(self):
        eye = HuginnEye()
        eval_res = eye.evaluate("ANJING!")
        # 6 letters all-caps with exclamation must trigger shouting arousal
        assert eval_res.shouting_score > 0.0

    def test_evaluation_result_policy_name_and_timestamp(self):
        guard = RavenGuard(ledger="memory")
        res = guard.process_turn("user_audit", "Halo bot")
        assert res.policy_name == "default"
        assert res.timestamp > 0.0
