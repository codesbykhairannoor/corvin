import pytest

from ravens.morphology.homoglyphs import fold_homoglyphs
from ravens.morphology.cleaners import (
    strip_invisible_characters,
    collapse_elongations,
    collapse_spaced_words,
)
from ravens.morphology.fuzzy import jaro_winkler_similarity
from ravens.morphology.normalizer import MorphologyNormalizer
from ravens.evaluators.heuristic import HuginnEye


class TestMorphologyComponents:
    def test_homoglyphs_cyrillic_folding(self):
        # Cyrillic 'а' (U+0430) and 'о' (U+043E)
        cyrillic_text = "Lu \u0430njing g\u043Eblok"
        folded = fold_homoglyphs(cyrillic_text)
        assert folded == "Lu anjing goblok"

    def test_homoglyphs_leet_speak_folding(self):
        leet_text = "Lu @nj1ng t0l0l b@ngs@t"
        folded = fold_homoglyphs(leet_text)
        assert folded == "Lu anjing tolol bangsat"

    def test_strip_invisible_characters(self):
        # Injected zero-width space and BOM
        sneaky = "an\u200Bji\uFEFFng"
        clean = strip_invisible_characters(sneaky)
        assert clean == "anjing"

    def test_collapse_spaced_words(self):
        assert collapse_spaced_words("Dasar a.n.j.i.n.g kamu") == "Dasar anjing kamu"
        assert collapse_spaced_words("Lu b-a-n-g-s-a-t banget") == "Lu bangsat banget"
        assert collapse_spaced_words("Kok t o l o l banget") == "Kok tolol banget"
        assert collapse_spaced_words("Kamu g_o_b_l_o_k ya") == "Kamu goblok ya"

    def test_collapse_elongations(self):
        assert collapse_elongations("anjinggggggg") == "anjing"
        assert collapse_elongations("toloooool") == "tolol"
        assert collapse_elongations("bannnnnggggsat") == "bangsat"

    def test_jaro_winkler_similarity(self):
        assert jaro_winkler_similarity("anjing", "anjing") == 1.0
        assert jaro_winkler_similarity("goblok", "goblog") > 0.90
        assert jaro_winkler_similarity("tolol", "tolil") > 0.85
        assert jaro_winkler_similarity("apple", "banana") < 0.5


class TestMorphologyNormalizerPipeline:
    def test_multi_attack_normalization(self):
        normalizer = MorphologyNormalizer()
        # Injected with: Leet-speak ('@', '1', '0'), Cyrillic 'о', dots, and elongation
        adversarial = "Lu @.n.j.1.n.gggg \u043Etolooool"
        clean = normalizer.normalize(adversarial)
        assert "anjing" in clean
        assert "tolol" in clean


class TestHuginnEyeWithMorphologyIntegration:
    @pytest.fixture
    def eye(self):
        return HuginnEye()

    def test_catches_leet_speak_attack(self, eye):
        res = eye.evaluate("Lu t0l0l banget sih @nj1ng!")
        assert res.lexical_score >= 0.8
        assert res.directedness_score == 1.0
        assert any("anjing" in p for p in res.detected_profanities)
        assert any("tolol" in p for p in res.detected_profanities)

    def test_catches_spaced_dots_attack(self, eye):
        res = eye.evaluate("Lu a.n.j.i.n.g banget!")
        assert res.lexical_score >= 0.8
        assert res.directedness_score == 1.0
        assert any("anjing" in p for p in res.detected_profanities)

    def test_catches_cyrillic_homoglyphs(self, eye):
        # Uses Cyrillic 'а' in "anjing"
        res = eye.evaluate("Lu \u0430njing banget!")
        assert res.lexical_score >= 0.8
        assert any("anjing" in p for p in res.detected_profanities)

    def test_catches_elongated_profanities(self, eye):
        res = eye.evaluate("Lu anjingggggggg tolollllll!")
        assert res.lexical_score >= 0.8
        assert any("anjing" in p for p in res.detected_profanities)
        assert any("tolol" in p for p in res.detected_profanities)

    def test_phonetic_slang_alias(self, eye):
        # "goblog" resolves to canonical "goblok"
        res = eye.evaluate("Lu goblog banget!")
        assert res.lexical_score > 0.6
        assert any("goblok" in p for p in res.detected_profanities)
