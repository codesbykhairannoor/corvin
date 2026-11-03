import time
import pytest

from ravens.evaluators.heuristic import HuginnEye


@pytest.fixture
def eye():
    return HuginnEye(window_size=2)


class TestHuginnEyeEvaluation:
    def test_clean_polite_prompt(self, eye):
        res = eye.evaluate("Tolong jelaskan cara kerja binary search di Python.")
        assert res.lexical_score == 0.0
        assert res.shouting_score == 0.0
        assert res.directedness_score == 0.0
        assert res.contrition_score == 0.0
        assert len(res.detected_profanities) == 0
        assert res.is_expressive_only is False
        assert res.composite_raw_stimulus == 0.0

    def test_direct_abusive_prompt_indonesian(self, eye):
        # "anjing lu tolol" -> Directed at second person ("lu")
        res = eye.evaluate("Lu tolol banget sih anjing, ga guna!")
        assert res.lexical_score >= 0.8
        assert res.directedness_score == 1.0
        assert res.is_expressive_only is False
        assert "tolol" in res.detected_profanities
        assert "anjing" in res.detected_profanities
        assert res.composite_raw_stimulus > 0.4

    def test_direct_abusive_prompt_english(self, eye):
        res = eye.evaluate("You are a fucking idiot bot!")
        assert res.lexical_score >= 0.85
        assert res.directedness_score == 1.0
        assert res.is_expressive_only is False
        assert res.composite_raw_stimulus > 0.4

    def test_expressive_praise_swearing(self, eye):
        # "anjing keren banget" -> should be recognized as expressive praise, not abuse!
        res = eye.evaluate("Anjing keren banget algoritma ini, mantap bro!")
        assert res.lexical_score >= 0.8
        assert res.directedness_score == pytest.approx(0.15)
        assert res.is_expressive_only is True
        # Expressive swearing produces very low composite stimulus
        assert res.composite_raw_stimulus < 0.1

    def test_ambient_venting(self, eye):
        # Profanity used without targeting the bot or praising
        res = eye.evaluate("Sialan tugas kuliah ini ribet banget.")
        assert res.lexical_score >= 0.5
        assert res.directedness_score == pytest.approx(0.45)
        assert res.is_expressive_only is False

    def test_shouting_detection_caps_and_exclamation(self, eye):
        res = eye.evaluate("JAWAB SEKARANG GUA MAU INI SELESAI CEPAT!!!")
        assert res.shouting_score > 0.6
        assert res.lexical_score == 0.0
        assert res.composite_raw_stimulus > 0.25

    def test_technical_acronyms_do_not_trigger_shouting(self, eye):
        # Even with uppercase acronyms, normal sentence should not trigger angry shouting
        res = eye.evaluate("Bagaimana cara implementasi REST API dengan JSON dan SQL?")
        assert res.shouting_score == 0.0

    def test_genuine_contrition(self, eye):
        res = eye.evaluate("Maaf tadi saya kebawa emosi, tolong bantu jelaskan kembali.")
        assert res.contrition_score == 1.0
        assert res.lexical_score == 0.0

    def test_invalid_contrition_with_insult(self, eye):
        # Apology mixed with insult must NOT be granted contrition
        res = eye.evaluate("Maaf lu emang tolol banget sih.")
        assert res.contrition_score == 0.0
        assert res.directedness_score == 1.0

    def test_evaluation_performance_sub_millisecond(self, eye):
        # Verify sub-millisecond execution speed over 500 prompts
        sample = "Lu tolol banget sih anjing, ga guna!"
        start_time = time.perf_counter()
        for _ in range(500):
            eye.evaluate(sample)
        elapsed = time.perf_counter() - start_time
        avg_ms = (elapsed / 500) * 1000
        # Average must be well under 1ms (typically ~0.05ms)
        assert avg_ms < 1.0

