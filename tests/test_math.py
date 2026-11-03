import math
import pytest

from ravens.math.decay import (
    calculate_grudge_decay,
    patience_from_grudge,
    grudge_from_patience,
)
from ravens.math.friction import calculate_synthetic_delay
from ravens.math.scoring import (
    calculate_recidivism_multiplier,
    calculate_stimulus,
)


class TestAffectiveDecay:
    def test_zero_elapsed_time_preserves_grudge(self):
        grudge = 80.0
        decayed = calculate_grudge_decay(initial_grudge=grudge, elapsed_seconds=0.0)
        assert decayed == pytest.approx(80.0)

    def test_negative_elapsed_time_preserves_grudge(self):
        grudge = 50.0
        decayed = calculate_grudge_decay(initial_grudge=grudge, elapsed_seconds=-100.0)
        assert decayed == pytest.approx(50.0)

    def test_half_life_exact_halving(self):
        """
        At t = t_half, grudge must decay to exactly 50% of its initial value
        according to the exponential decay equation: G(t_half) = G_0 * e^(-ln(2)) = G_0 / 2.
        """
        initial_grudge = 80.0
        half_life = 3600.0  # 1 hour
        decayed = calculate_grudge_decay(
            initial_grudge=initial_grudge,
            elapsed_seconds=half_life,
            half_life_seconds=half_life,
        )
        assert decayed == pytest.approx(40.0, rel=1e-5)

    def test_two_half_lives_quarters_grudge(self):
        """
        At t = 2 * t_half, grudge should be 25% of initial value.
        """
        initial_grudge = 100.0
        half_life = 1800.0
        decayed = calculate_grudge_decay(
            initial_grudge=initial_grudge,
            elapsed_seconds=2 * half_life,
            half_life_seconds=half_life,
        )
        assert decayed == pytest.approx(25.0, rel=1e-5)

    def test_invalid_half_life_raises_value_error(self):
        with pytest.raises(ValueError):
            calculate_grudge_decay(initial_grudge=50.0, elapsed_seconds=10.0, half_life_seconds=0.0)

    def test_patience_grudge_inversion(self):
        assert patience_from_grudge(0.0) == 100.0
        assert patience_from_grudge(100.0) == 0.0
        assert patience_from_grudge(35.0) == 65.0
        assert grudge_from_patience(65.0) == 35.0


class TestSyntheticFriction:
    def test_receptive_zone_has_zero_delay(self):
        # Above threshold_upper (50.0), delay is always 0.0
        assert calculate_synthetic_delay(patience=100.0) == 0.0
        assert calculate_synthetic_delay(patience=75.0) == 0.0
        assert calculate_synthetic_delay(patience=50.0) == 0.0

    def test_strike_zone_has_max_delay(self):
        # Below or at threshold_lower (25.0), delay is max (15.0)
        assert calculate_synthetic_delay(patience=25.0) == 15.0
        assert calculate_synthetic_delay(patience=10.0) == 15.0
        assert calculate_synthetic_delay(patience=0.0) == 15.0

    def test_quadratic_curve_midpoint(self):
        """
        Midpoint between 50 and 25 is 37.5.
        Normalized distance: (50 - 37.5) / 25 = 0.5.
        Quadratic delay: 15 * (0.5^2) = 15 * 0.25 = 3.75s.
        """
        delay = calculate_synthetic_delay(patience=37.5, max_delay_seconds=15.0)
        assert delay == pytest.approx(3.75, rel=1e-5)

    def test_invalid_thresholds_raise_error(self):
        with pytest.raises(ValueError):
            calculate_synthetic_delay(patience=40.0, threshold_upper=25.0, threshold_lower=50.0)


class TestScoringAndRecidivism:
    def test_recidivism_multiplier_zero_infractions(self):
        # Gamma(0) = 1.0 + beta * ln(1) = 1.0
        assert calculate_recidivism_multiplier(0) == pytest.approx(1.0)

    def test_recidivism_multiplier_positive_infractions(self):
        # Gamma(3) = 1.0 + 0.5 * ln(4) = 1.0 + 0.5 * 1.38629 = 1.6931
        expected = 1.0 + 0.5 * math.log(4.0)
        assert calculate_recidivism_multiplier(3) == pytest.approx(expected, rel=1e-5)

    def test_stimulus_zero_inputs(self):
        stimulus = calculate_stimulus(
            lexical_score=0.0,
            shouting_score=0.0,
            directedness_score=0.0,
        )
        assert stimulus == 0.0

    def test_stimulus_full_toxicity_no_infractions(self):
        # Raw = 35*1 + 20*1 + 25*1 = 80.0. Gamma(0) = 1.0. Total = 80.0
        stimulus = calculate_stimulus(
            lexical_score=1.0,
            shouting_score=1.0,
            directedness_score=1.0,
            prior_infractions=0,
        )
        assert stimulus == pytest.approx(80.0)

    def test_stimulus_with_recidivism_clamped_to_100(self):
        # Raw = 80.0. With 10 prior infractions, Gamma(10) = 1.0 + 0.5*ln(11) = 2.1989
        # 80.0 * 2.1989 = 175.9 -> must be clamped to 100.0
        stimulus = calculate_stimulus(
            lexical_score=1.0,
            shouting_score=1.0,
            directedness_score=1.0,
            prior_infractions=10,
        )
        assert stimulus == 100.0

