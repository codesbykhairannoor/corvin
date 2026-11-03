import math

def calculate_grudge_decay(
    initial_grudge: float,
    elapsed_seconds: float,
    half_life_seconds: float = 3600.0,
    baseline: float = 0.0,
) -> float:
    """
    Computes exponential emotional decay based on the affective dynamics
    formulation by Picard (1997) & Marsella & Gratch (EMA 2009).

    Formula:
        G(t) = G_0 + (G_init - G_0) * e^(-lambda * delta_t)
        where lambda = ln(2) / half_life_seconds

    Args:
        initial_grudge: The grudge score at the last recorded interaction (0.0 to 100.0).
        elapsed_seconds: Number of seconds elapsed since the last interaction.
        half_life_seconds: Time in seconds for the grudge to decay by 50% without new stimuli.
                           Default: 3600s (1 hour).
        baseline: Baseline resting grudge level (default: 0.0).

    Returns:
        float: Decayed grudge value in [0.0, 100.0].
    """
    if elapsed_seconds <= 0.0:
        return max(0.0, min(100.0, initial_grudge))
    if initial_grudge <= baseline:
        return baseline
    if half_life_seconds <= 0.0:
        raise ValueError("half_life_seconds must be strictly positive.")

    decay_constant = math.log(2) / half_life_seconds
    decayed = baseline + (initial_grudge - baseline) * math.exp(-decay_constant * elapsed_seconds)
    return max(0.0, min(100.0, decayed))


def patience_from_grudge(grudge: float) -> float:
    """
    Converts a grudge index (0 = zero hostility, 100 = maximum rage)
    into a patience index (100 = fully cooperative, 0 = total refusal).

    P = 100 - G
    """
    clamped_grudge = max(0.0, min(100.0, grudge))
    return 100.0 - clamped_grudge


def grudge_from_patience(patience: float) -> float:
    """
    Converts a patience index (100 to 0) into a grudge index (0 to 100).

    G = 100 - P
    """
    clamped_patience = max(0.0, min(100.0, patience))
    return 100.0 - clamped_patience

