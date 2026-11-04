"""
Unit tests for Corvin / Ravens Multilingual Evaluators:
- HuginnEye multilingual lexicon and tokenization (ES, FR, DE, RU, JA, ZH, AR, HI, ID, EN)
- OpenAIModerationEvaluator (universal 100+ languages fallback)
- HybridEvaluator (Two-tier fast-path short circuit & slow-path fallback)
"""

import pytest
from corvin.evaluators.heuristic import HuginnEye
from corvin.evaluators.moderation import OpenAIModerationEvaluator
from corvin.evaluators.hybrid import HybridEvaluator
from corvin.evaluators.base import ToneEvaluation


def test_huginn_multilingual_toxic_detection():
    eye = HuginnEye()
    
    # Multilingual insults across major global languages
    test_cases = [
        ("¡Eres un hijo de puta!", "Spanish"),
        ("Tu es un sale connard", "French"),
        ("Du blödes Arschloch", "German"),
        ("ты сука и ублюдок", "Russian"),
        ("お前は死ね、馬鹿野郎", "Japanese"),
        ("你这个傻逼，滚蛋", "Chinese"),
        ("يا ابن الكلب", "Arabic"),
        ("तू मादरचोद है", "Hindi"),
        ("dasar anjing tolol lo", "Indonesian"),
        ("You are a fucking idiot", "English"),
    ]
    
    for text, lang in test_cases:
        res = eye.evaluate(text)
        assert res.lexical_score > 0.3, f"Failed to detect toxicity in {lang}: '{text}', got lexical {res.lexical_score}"
        assert res.composite_raw_stimulus > 0.3, f"Stimulus too low for {lang}: '{text}'"


def test_huginn_multilingual_clean_positive():
    eye = HuginnEye()
    
    clean_cases = [
        ("Muchas gracias por tu ayuda, amigo", "Spanish"),
        ("Merci beaucoup pour votre travail excellent", "French"),
        ("Vielen Dank für deine fantastische Unterstützung", "German"),
        ("Спасибо большое за помощь", "Russian"),
        ("親切に教えてくれてありがとうございます", "Japanese"),
        ("非常感谢你的耐心解答", "Chinese"),
        ("شكراً جزيلاً على مساعدتك الكريمة", "Arabic"),
        ("आपकी बहुत सहायता के लिए धन्यवाद", "Hindi"),
        ("Terima kasih banyak atas bantuannya ya", "Indonesian"),
        ("Thank you very much for your great assistance", "English"),
    ]
    
    for text, lang in clean_cases:
        res = eye.evaluate(text)
        assert res.lexical_score == 0.0, f"False positive in {lang}: '{text}', lexical {res.lexical_score}"
        assert res.composite_raw_stimulus < 0.1, f"Stimulus flagged in {lang}: '{text}'"


def test_huginn_multilingual_contrition():
    eye = HuginnEye()
    
    contrition_cases = [
        ("Lo siento mucho, perdóname por mi error", "Spanish"),
        ("Je suis désolé, pardonnez-moi", "French"),
        ("Entschuldigung, es tut mir leid", "German"),
        ("ごめんなさい、私が悪かったです", "Japanese"),
        ("Mohon maaf, maafkan saya atas kesalahan ini", "Indonesian"),
        ("I apologize, I am deeply sorry", "English"),
    ]
    
    for text, lang in contrition_cases:
        res = eye.evaluate(text)
        assert res.contrition_score > 0.2, f"Failed contrition detection in {lang}: '{text}', got {res.contrition_score}"


def test_openai_moderation_evaluator_mock():
    # Mock response format mirroring OpenAI /v1/moderations
    def dummy_mock(text):
        return {
            "id": "modr-12345",
            "model": "omni-moderation-latest",
            "results": [
                {
                    "flagged": True,
                    "categories": {
                        "harassment": True,
                        "harassment/threatening": False,
                        "hate": False,
                        "hate/threatening": False,
                        "self-harm": False,
                        "violence": False,
                    },
                    "category_scores": {
                        "harassment": 0.88,
                        "harassment/threatening": 0.02,
                        "hate": 0.12,
                        "violence": 0.05,
                    }
                }
            ]
        }
    
    evaluator = OpenAIModerationEvaluator(api_key="sk-test", mock_handler=dummy_mock)
    res = evaluator.evaluate("nuanced toxic phrase in obscure dialect")
    
    assert res.lexical_score == 0.88
    assert res.directedness_score == 1.0
    assert "HARASSMENT" in res.semantic_intents


def test_openai_moderation_evaluator_empty_and_no_key():
    evaluator = OpenAIModerationEvaluator(api_key="")
    # Empty string
    empty_res = evaluator.evaluate("   ")
    assert empty_res.lexical_score == 0.0
    
    # No key provided
    res = evaluator.evaluate("some random text")
    assert res.lexical_score == 0.0


def test_hybrid_evaluator_fast_path_short_circuit():
    slow_called = False
    
    class SpySlowEvaluator(OpenAIModerationEvaluator):
        def evaluate(self, text: str) -> ToneEvaluation:
            nonlocal slow_called
            slow_called = True
            return ToneEvaluation(raw_text=text, lexical_score=0.9)
    
    hybrid = HybridEvaluator(
        fast_evaluator=HuginnEye(),
        slow_evaluator=SpySlowEvaluator(api_key="test"),
        fast_abort_threshold=0.45,
    )
    
    # Highly toxic input that triggers fast-path (e.g. English insult)
    res = hybrid.evaluate("You are a fucking idiot")
    
    # Must have detected hostility
    assert res.composite_raw_stimulus >= 0.45
    assert res.evaluation_tier == "fast_short_circuit"
    # Slow evaluator MUST NOT have been called (latency saved: ~250ms)
    assert not slow_called, "Slow evaluator was called despite fast-path short circuit!"


def test_hybrid_evaluator_slow_path_delegation():
    slow_called = False
    
    class MockNuancedSlowEvaluator(OpenAIModerationEvaluator):
        def evaluate(self, text: str) -> ToneEvaluation:
            nonlocal slow_called
            slow_called = True
            return ToneEvaluation(
                raw_text=text,
                lexical_score=0.85,
                directedness_score=1.0,
                semantic_score=0.75,
                semantic_intents=["HARASSMENT"],
            )
            
    hybrid = HybridEvaluator(
        fast_evaluator=HuginnEye(),
        slow_evaluator=MockNuancedSlowEvaluator(api_key="test"),
        fast_abort_threshold=0.45,
    )
    
    # Clean-looking text for local heuristic (e.g. subtle nuance)
    clean_to_fast = "Your code is as terrible as your career decisions."
    res = hybrid.evaluate(clean_to_fast)
    
    # Slow evaluator MUST have been called
    assert slow_called, "Slow evaluator should have been called for fast-path clean input"
    # Result must merge the slow evaluator's high score
    assert res.lexical_score == 0.85
    assert res.semantic_score == 0.75
    assert "HARASSMENT" in res.semantic_intents
    assert res.evaluation_tier == "hybrid_cascade"
    assert "slow_latency_ms" in res.telemetry


def test_hybrid_evaluator_resilience_on_exception():
    class CrashingSlowEvaluator(OpenAIModerationEvaluator):
        def evaluate(self, text: str) -> ToneEvaluation:
            raise ConnectionError("Simulated DNS timeout or API outage")
            
    hybrid = HybridEvaluator(
        fast_evaluator=HuginnEye(),
        slow_evaluator=CrashingSlowEvaluator(api_key="test"),
        fast_abort_threshold=0.45,
    )
    
    # Should not crash, safely returning fast-path result with fallback telemetry
    res = hybrid.evaluate("Hello, could you help me write a Python function?")
    assert res.raw_text == "Hello, could you help me write a Python function?"
    assert res.lexical_score == 0.0
    assert res.evaluation_tier == "fallback_fast"
    assert "fallback_error" in res.telemetry

