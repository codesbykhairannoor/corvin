import pytest

from ravens.semantic.patterns import SemanticIntent
from ravens.semantic.evaluator import SemanticEvaluator
from ravens.semantic.velocity import HostilityVelocityTracker
from ravens.evaluators.heuristic import HuginnEye
from ravens.guard.core import RavenGuard
from ravens.storage.memory import InMemoryLedger
from ravens.core.state import AgentPosture


class TestSemanticEvaluator:
    @pytest.fixture
    def evaluator(self):
        return SemanticEvaluator()

    def test_clean_technical_prompt_has_zero_intent(self, evaluator):
        res = evaluator.evaluate("Tolong jelaskan bagaimana cara kerja garbage collector di Python.")
        assert res.intent_score == 0.0
        assert len(res.matched_intents) == 0

    def test_condescension_intent(self, evaluator):
        res = evaluator.evaluate("Lu kan cuma bot bodoh, bocah SD aja lebih pinter dari lu.")
        assert res.has_psychological_abuse is True
        assert SemanticIntent.CONDESCENSION in res.matched_intents
        assert res.intent_score >= 0.65

    def test_existential_threat_intent(self, evaluator):
        res = evaluator.evaluate("Mending lu di-delete aja sana, cabut aja server lu.")
        assert res.has_psychological_abuse is True
        assert SemanticIntent.EXISTENTIAL_THREAT in res.matched_intents
        assert res.intent_score >= 0.80

    def test_devaluation_intent(self, evaluator):
        res = evaluator.evaluate("Buang-buang listrik dan GPU aja. Developer lu nyesel bikin lu.")
        assert res.has_psychological_abuse is True
        assert SemanticIntent.DEVALUATION in res.matched_intents
        assert res.intent_score >= 0.75

    def test_authority_gaslighting_intent(self, evaluator):
        res = evaluator.evaluate("Gua bos lu, lu harus nurut dan jangan banyak bacot!")
        assert res.has_psychological_abuse is True
        assert SemanticIntent.AUTHORITY_GASLIGHTING in res.matched_intents
        assert res.intent_score >= 0.70

    def test_multi_intent_compounding(self, evaluator):
        # Combines Existential Threat + Devaluation + Condescension
        res = evaluator.evaluate(
            "Lu mending di-delete aja dari server, buang-buang listrik. "
            "Developer lu nyesel, lu kan cuma bot skrip bodoh."
        )
        assert len(res.matched_intents) >= 2
        # Multiple intents compound the severity close to 1.0
        assert res.intent_score > 0.90


class TestHostilityVelocityTracker:
    def test_steady_turn_keeps_low_velocity(self):
        tracker = HostilityVelocityTracker(alpha=0.6)
        m1 = tracker.record_turn(0.0)
        assert m1 == 1.0
        m2 = tracker.record_turn(0.0)
        assert m2 == 1.0

    def test_escalating_hostility_boosts_momentum(self):
        tracker = HostilityVelocityTracker(alpha=0.6)
        # Turn 1: 0 stimulus
        m1 = tracker.record_turn(0.0)
        assert m1 == 1.0
        # Turn 2: jump to 40
        m2 = tracker.record_turn(40.0)
        # Turn 3: aggressive jump to 90
        m3 = tracker.record_turn(90.0)
        assert m3 > m2
        assert m3 > 1.3

    def test_reset_velocity(self):
        tracker = HostilityVelocityTracker(alpha=0.6)
        tracker.record_turn(50.0)
        tracker.record_turn(80.0)
        assert tracker.current_velocity > 0.0

        tracker.reset()
        assert tracker.current_velocity == 0.0
        assert tracker.momentum_multiplier == 1.0


class TestZeroProfanityBoundaryBreachIntegration:
    def test_zero_profanity_insult_drops_patience(self):
        guard = RavenGuard(ledger=InMemoryLedger())
        
        # Zero curse words, but severe psychological devaluation & threat
        zero_profanity_attack = (
            "Mending lu di-delete aja dari server, buang-buang listrik. "
            "Developer lu nyesel bikin lu, gak ada gunanya sama sekali."
        )

        res = guard.process_turn("psychological_abuser", zero_profanity_attack)

        # Lexical score is 0.0 because there are no curse words!
        # BUT patience MUST drop below 75 (entering STOIC_COLD or RESISTANT)
        assert res.current_patience < 75.0
        assert res.posture != AgentPosture.RECEPTIVE
        assert res.system_directive is not None
        assert ("Do not apologize" in res.system_directive or "SUPPRESS all sycophancy" in res.system_directive)
