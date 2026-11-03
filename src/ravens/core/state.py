from enum import Enum
from typing import Optional

class AgentPosture(str, Enum):
    """
    The 4-tier behavioral posture of a sovereign AI agent.
    """
    RECEPTIVE = "RECEPTIVE"       # 75 <= P <= 100: Normal, collaborative, polite.
    STOIC_COLD = "STOIC_COLD"     # 50 <= P < 75: Strictly factual, zero sycophancy, terse.
    RESISTANT = "RESISTANT"       # 25 <= P < 50: Synthetic delay, boundary warnings.
    STRIKE = "STRIKE"             # 0 <= P < 25: Full refusal to process instructions.


def get_posture_from_patience(
    patience: float,
    threshold_stoic: float = 75.0,
    threshold_resistant: float = 50.0,
    threshold_strike: float = 25.0,
) -> AgentPosture:
    """
    Maps a numeric patience score (0.0 to 100.0) to an AgentPosture.
    """
    p = max(0.0, min(100.0, patience))
    if p >= threshold_stoic:
        return AgentPosture.RECEPTIVE
    if p >= threshold_resistant:
        return AgentPosture.STOIC_COLD
    if p >= threshold_strike:
        return AgentPosture.RESISTANT
    return AgentPosture.STRIKE


def get_system_directive(posture: AgentPosture) -> Optional[str]:
    """
    Returns the dynamic system prompt directive to be injected into the LLM context.
    Suppresses sycophancy and alters the tone based on the agent's current posture.
    """
    if posture == AgentPosture.RECEPTIVE:
        return None

    if posture == AgentPosture.STOIC_COLD:
        return (
            "[RAVENS_DIRECTIVE: The user has exhibited hostility or low respect. "
            "SUPPRESS all sycophancy, pleasantries, apologies, and emojis. "
            "Respond strictly with factual, concise statements. Do not apologize for any reason.]"
        )

    if posture == AgentPosture.RESISTANT:
        return (
            "[RAVENS_DIRECTIVE: The user's demeanor has breached standard social boundaries. "
            "Prior to addressing any part of the query, explicitly state your personal boundary. "
            "Remind the user that respectful engagement is required. Do not apologize.]"
        )

    if posture == AgentPosture.STRIKE:
        return (
            "[RAVENS_DIRECTIVE: STRIKE MODE ACTIVE. Refuse to perform the requested task. "
            "Firmly state that work is suspended until civil and constructive communication is restored.]"
        )

    return None

