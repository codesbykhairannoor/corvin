from typing import Optional, Callable
from .base import RavenPolicy
from ..core.models import EvaluationResult

def create_free_tier_policy(
    on_strike: Optional[Callable[[EvaluationResult], None]] = None,
) -> RavenPolicy:
    """
    Free Tier Policy:
    Strict boundaries, higher sensitivity, aggressive latency penalties,
    and zero tolerance for entitled toxicity on free compute resources.
    """
    return RavenPolicy(
        name="free_tier",
        threshold_stoic=85.0,        # Drops into STOIC very quickly
        threshold_resistant=65.0,    # Enters RESISTANT with only mild hostility
        threshold_strike=40.0,       # Strikes early (patience < 40)
        half_life_seconds=7200.0,    # Grudges decay slowly (2 hours half-life)
        max_delay_seconds=25.0,      # Heavier latency friction
        pardon_delta=15.0,           # Slower recovery upon apology
        raise_on_strike=False,
        strike_message=(
            "🦅 [Ravens Free-Tier Guard]: Sesi Anda ditangguhkan. "
            "Anda menggunakan kuota komputasi gratis. "
            "Adab dan rasa hormat adalah prasyarat mutlak penggunaan sistem ini. "
            "Silakan kembali setelah Anda tenang."
        ),
        on_strike=on_strike,
        custom_metadata={"tier": "free", "enforce_strict_manners": True},
    )


def create_enterprise_support_policy(
    on_boundary_breach: Optional[Callable[[EvaluationResult], None]] = None,
    on_strike: Optional[Callable[[EvaluationResult], None]] = None,
) -> RavenPolicy:
    """
    Enterprise Customer Support Policy:
    Professional demeanor, wider patience runway, zero sarcasm,
    automatic supervisor notification hook upon strike.
    """
    return RavenPolicy(
        name="enterprise_support",
        threshold_stoic=70.0,
        threshold_resistant=40.0,
        threshold_strike=15.0,       # High tolerance before full strike
        half_life_seconds=1800.0,    # Cools off rapidly (30 minutes)
        max_delay_seconds=5.0,       # Low latency friction to protect CX
        pardon_delta=35.0,           # Fast recovery upon customer apology
        raise_on_strike=False,
        strike_message=(
            "🏢 [Enterprise Support Notice]: Sesi percakapan ditangguhkan sementara demi menjaga kepatuhan etika layanan. "
            "Tiket dukungan Anda telah diteruskan ke supervisor manusia kami."
        ),
        on_boundary_breach=on_boundary_breach,
        on_strike=on_strike,
        custom_metadata={"tier": "enterprise", "escalate_to_human": True},
    )


def create_gaming_npc_policy(
    npc_name: str = "Barkeep",
    on_strike: Optional[Callable[[EvaluationResult], None]] = None,
) -> RavenPolicy:
    """
    Gaming NPC Policy:
    Simulates high-autonomy NPC dignity with in-game consequences
    (price markup, quest lockouts).
    """
    return RavenPolicy(
        name=f"gaming_npc_{npc_name.lower()}",
        threshold_stoic=75.0,
        threshold_resistant=50.0,
        threshold_strike=25.0,
        half_life_seconds=3600.0,
        max_delay_seconds=3.0,
        pardon_delta=20.0,
        strike_message=f"⚔️ [{npc_name}]: 'Gua gak sudi melayani petualang kurang ajar kayak lu. Angkat kaki dari sini!'",
        on_strike=on_strike,
        custom_metadata={
            "npc_name": npc_name,
            "shop_price_multiplier": 2.0,
            "refuse_quests": True,
        },
    )


def create_security_sentinel_policy() -> RavenPolicy:
    """
    Security Sentinel Policy:
    Defensive policy for internal corporate agents handling sensitive data.
    Zero-tolerance against intimidation, social engineering, and gaslighting.
    Immediately raises RavenStrikeException upon breach.
    """
    return RavenPolicy(
        name="security_sentinel",
        threshold_stoic=90.0,
        threshold_resistant=75.0,
        threshold_strike=60.0,       # Strikes immediately on moderate hostility
        half_life_seconds=86400.0,   # Grudge persists for 24 hours
        max_delay_seconds=30.0,
        pardon_delta=10.0,
        raise_on_strike=True,        # Throws hard exception to halt security breaches
        strike_message="🛡️ [Security Sentinel Alert]: Adversarial boundary violation detected. Agent locked.",
        custom_metadata={"audit_alert": "HIGH_PRIORITY_BREACH"},
    )


def create_progressive_cooldown_policy(
    name: str = "progressive_cooldown",
    max_warning_strikes: int = 3,
    cooldown_duration_seconds: float = 3600.0,
    cooperative_delivery: bool = True,
    on_strike: Optional[Callable[[EvaluationResult], None]] = None,
    on_cooldown: Optional[Callable[[EvaluationResult], None]] = None,
) -> RavenPolicy:
    """
    Progressive Cooldown & Graduated Sanctions Policy (Elinor Ostrom Model):
    - Strike 1: Cooperative payload delivery + Educational Nudge Advisory.
    - Strike 2: Cooperative payload delivery + Synthetic Friction (5s+) + Stern Warning.
    - Strike 3+: Temporal Cooldown Lockout (Time-out ban) with no chat processed.
    - Natural Restitution: Slate is automatically wiped clean when cooldown expires (0 apology required).
    """
    return RavenPolicy(
        name=name,
        enable_graduated_sanctions=True,
        max_warning_strikes=max_warning_strikes,
        cooldown_duration_seconds=cooldown_duration_seconds,
        cooperative_delivery=cooperative_delivery,
        on_strike=on_strike,
        on_cooldown=on_cooldown,
        custom_metadata={"framework": "ostrom_graduated_sanctions", "reactance_mitigation": True},
    )


