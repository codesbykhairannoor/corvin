def jaro_winkler_similarity(s1: str, s2: str, prefix_weight: float = 0.1) -> float:
    """
    Computes the Jaro-Winkler string similarity between two strings s1 and s2.
    Returns a score between 0.0 (completely dissimilar) and 1.0 (exact match).
    
    Standardized algorithm:
    - Jaro distance accounts for character matches and transpositions.
    - Winkler prefix adjustment increases score if strings share a common initial prefix.
    """
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    # Maximum matching distance
    match_bound = max(len1, len2) // 2 - 1
    if match_bound < 0:
        match_bound = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    transpositions = 0

    # 1. Identify matches
    for i in range(len1):
        start = max(0, i - match_bound)
        end = min(i + match_bound + 1, len2)

        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    # 2. Count transpositions
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    transpositions = transpositions // 2

    # Jaro calculation
    jaro = (
        (matches / len1) +
        (matches / len2) +
        ((matches - transpositions) / matches)
    ) / 3.0

    # 3. Winkler prefix bonus (up to 4 matching characters at start)
    prefix_len = 0
    max_prefix = min(4, min(len1, len2))
    for i in range(max_prefix):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break

    jaro_winkler = jaro + (prefix_len * prefix_weight * (1.0 - jaro))
    return min(1.0, max(0.0, jaro_winkler))

