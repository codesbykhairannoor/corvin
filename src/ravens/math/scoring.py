import math

def calculate_recidivism_multiplier(prior_infractions: int, beta: float = 0.5) -> float:
    """
    Computes a recidivism scaling factor Gamma(k) for repeat offenders.
    
    Formula:
        Gamma(k) = 1.0 + beta * ln(1 + k)
    
    Where:
        k is the count of prior severe infractions recorded in the Ledger.
        beta is the scaling sensitivity (default: 0.5).

    Args:
        prior_infractions: Number of previous boundary violations.
        beta: Growth rate parameter (default: 0.5).

    Returns:
        float: Multiplier >= 1.0.
    """
    k = max(0, prior_infractions)
    return 1.0 + beta * math.log(1.0 + k)


def calculate_stimulus(
    lexical_score: float,
    shouting_score: float,
    directedness_score: float,
    semantic_score: float = 0.0,
    prior_infractions: int = 0,
    weight_lex: float = 35.0,
    weight_caps: float = 20.0,
    weight_target: float = 25.0,
    weight_semantic: float = 45.0,
    beta: float = 0.5,
) -> float:
    """
    Computes the total incoming toxic stimulus S(x_t) of an interaction.
    Incorporates both overt lexical attacks and zero-profanity semantic psychological abuse.
    
    Formula:
        Lexical_Branch = (w_lex * L + w_caps * C + w_target * T)
        Semantic_Branch = w_semantic * Semantic_Score
        Raw_Score = max(Lexical_Branch, Semantic_Branch)
        S(x_t) = Raw_Score * Gamma(Recidivism)

    Args:
        lexical_score: Normalized toxicity rating from lexicon (0.0 to 1.0).
        shouting_score: Normalized typographical arousal / ALL CAPS ratio (0.0 to 1.0).
        directedness_score: Degree to which profanity is targeted at the agent/person (0.0 to 1.0).
        semantic_score: Severity rating for zero-profanity psychological abuse (0.0 to 1.0).
        prior_infractions: Count of previous infractions for recidivism escalation.

    Returns:
        float: Stimulus value in [0.0, 100.0].
    """
    l_clamped = max(0.0, min(1.0, lexical_score))
    c_clamped = max(0.0, min(1.0, shouting_score))
    t_clamped = max(0.0, min(1.0, directedness_score))
    s_clamped = max(0.0, min(1.0, semantic_score))

    # Overt branch
    lexical_branch = (
        (weight_lex * l_clamped) +
        (weight_caps * c_clamped) +
        (weight_target * t_clamped)
    )

    # Covert semantic psychological branch
    semantic_branch = weight_semantic * s_clamped

    # Combine: take whichever hostility signal is stronger, or add baseline shouting if semantic
    if s_clamped > 0.0:
        raw_stimulus = max(lexical_branch, semantic_branch + (weight_caps * c_clamped * 0.5))
    else:
        raw_stimulus = lexical_branch

    multiplier = calculate_recidivism_multiplier(prior_infractions, beta=beta)
    total_stimulus = raw_stimulus * multiplier
    return max(0.0, min(100.0, total_stimulus))
