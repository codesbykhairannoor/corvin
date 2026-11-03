def calculate_synthetic_delay(
    patience: float,
    threshold_upper: float = 50.0,
    threshold_lower: float = 25.0,
    max_delay_seconds: float = 15.0,
) -> float:
    """
    Computes a synthetic friction latency (in seconds) based on quadratic penalty shaping.
    
    When an agent's patience drops into the resistant zone (between threshold_lower and threshold_upper),
    instead of throwing a hard exception, it introduces intentional cognitive friction to slow down
    hostile or aggressive inputs without dropping the connection immediately.

    Formula:
        If patience >= threshold_upper:
            delay = 0.0
        If patience <= threshold_lower:
            delay = max_delay_seconds
        If threshold_lower < patience < threshold_upper:
            normalized = (threshold_upper - patience) / (threshold_upper - threshold_lower)
            delay = max_delay_seconds * (normalized ** 2)

    Args:
        patience: Current patience index of the user (0.0 to 100.0).
        threshold_upper: The patience value above which delay is 0.0 (default: 50.0).
        threshold_lower: The patience value at or below which max delay is imposed (default: 25.0).
        max_delay_seconds: Maximum latency penalty in seconds (default: 15.0).

    Returns:
        float: Delay duration in seconds.
    """
    if threshold_lower >= threshold_upper:
        raise ValueError("threshold_lower must be strictly less than threshold_upper.")
    if max_delay_seconds < 0.0:
        raise ValueError("max_delay_seconds must be non-negative.")

    if patience >= threshold_upper:
        return 0.0
    if patience <= threshold_lower:
        return max_delay_seconds

    normalized = (threshold_upper - patience) / (threshold_upper - threshold_lower)
    return max_delay_seconds * (normalized ** 2)

