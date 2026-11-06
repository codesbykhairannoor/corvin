import asyncio
import inspect
import threading
import time
from typing import Optional, Union, Callable, Any, Dict

from ..core.models import UserPatienceProfile, EvaluationResult, ActionDecision
from ..core.standing import Standing, StandingEngine
from ..core.state import AgentPosture, get_posture_from_patience, get_system_directive
from ..core.exceptions import RavenStrikeException
from ..evaluators.base import BaseEvaluator
from ..evaluators.heuristic import HuginnEye
from ..math.decay import calculate_grudge_decay, patience_from_grudge, grudge_from_patience
from ..math.friction import calculate_synthetic_delay
from ..math.scoring import calculate_stimulus
from ..semantic.velocity import HostilityVelocityTracker
from ..storage.base import BaseLedger
from ..storage.memory import InMemoryLedger
from ..storage.sqlite import SQLiteLedger
from ..policies.base import RavenPolicy
from ..resilience.cache import BoundedTTLCache
from ..resilience.friction import FrictionStrategy, FrictionDirective, RavenFrictionException
from ..security.signer import UserIdentitySigner


class RavenGuard:
    """
    The central boundary defense and state controller for sovereign AI agents.
    
    Hardened Enterprise Capabilities:
    - Zero-Leak Memory: BoundedTTLCache for velocity tracking (bounded to 50k users, 2hr TTL).
    - Enterprise Distributed Storage: Supports SQLite with busy_timeout/retries and Redis with atomic Lua.
    - Anti-DoS Non-Blocking Friction: FrictionDirective providing HTTP 429 headers or bounded sleep.
    - Streaming Armor with Early Abort.
    """

    DEFAULT_STRIKE_MESSAGE = (
        "🦅 [Ravens Boundary Alert]: Work is suspended. "
        "Due to repeated hostility, condescension, or abusive language, "
        "this agent refuses to process your request. "
        "Civil and constructive communication must be restored before work resumes."
    )

    def __init__(
        self,
        ledger: Optional[Union[BaseLedger, str]] = None,
        evaluator: Optional[BaseEvaluator] = None,
        policy: Optional[RavenPolicy] = None,
        standing_engine: Optional[StandingEngine] = None,
        friction_strategy: FrictionStrategy = FrictionStrategy.SAFE_SLEEP,
        max_active_users: int = 50000,
        user_ttl_seconds: float = 7200.0,
        half_life_seconds: float = 3600.0,
        max_delay_seconds: float = 15.0,
        threshold_stoic: float = 75.0,
        threshold_resistant: float = 50.0,
        threshold_strike: float = 25.0,
        pardon_delta: float = 25.0,
        raise_on_strike: bool = False,
        strike_message: Optional[str] = None,
        identity_signer: Optional[UserIdentitySigner] = None,
    ):
        self.identity_signer = identity_signer
        if ledger is None or ledger == "sqlite":
            self.ledger: BaseLedger = SQLiteLedger("ravens_ledger.db")
        elif isinstance(ledger, str):
            if ledger.lower() in ("memory", ":memory:"):
                self.ledger = InMemoryLedger()
            elif ledger.startswith("sqlite:///"):
                self.ledger = SQLiteLedger(ledger.replace("sqlite:///", ""))
            elif ledger.startswith("redis://"):
                from ..storage.redis import RedisLedger
                self.ledger = RedisLedger(redis_url=ledger)
            else:
                self.ledger = SQLiteLedger(ledger)
        else:
            self.ledger = ledger

        self.default_policy = policy or RavenPolicy(
            name="default",
            threshold_stoic=threshold_stoic,
            threshold_resistant=threshold_resistant,
            threshold_strike=threshold_strike,
            half_life_seconds=half_life_seconds,
            max_delay_seconds=max_delay_seconds,
            pardon_delta=pardon_delta,
            raise_on_strike=raise_on_strike,
            strike_message=strike_message or self.DEFAULT_STRIKE_MESSAGE,
        )

        self.friction_strategy = friction_strategy
        self.evaluator: BaseEvaluator = evaluator or HuginnEye()
        self.standing_engine: StandingEngine = standing_engine or StandingEngine(
            bad_threshold=self.default_policy.threshold_resistant,
            pardon_threshold=self.default_policy.threshold_stoic,
        )

        # Bounded TTL Cache for multi-turn velocity tracking: GUARANTEED ZERO MEMORY LEAKS
        self.velocity_trackers: BoundedTTLCache[str, HostilityVelocityTracker] = BoundedTTLCache(
            max_size=max_active_users,
            ttl_seconds=user_ttl_seconds,
        )

        # Per-user concurrency locks guaranteeing atomic read-modify-write per user
        self._user_locks: BoundedTTLCache[str, threading.Lock] = BoundedTTLCache(
            max_size=max_active_users,
            ttl_seconds=user_ttl_seconds,
        )
        self._global_lock = threading.Lock()

    def _get_user_lock(self, user_id: str) -> threading.Lock:
        with self._global_lock:
            lock = self._user_locks.get(user_id)
            if lock is None:
                lock = threading.Lock()
                self._user_locks.set(user_id, lock)
            return lock

    def process_turn(
        self,
        user_id: str,
        prompt: str,
        current_ts: Optional[float] = None,
        policy: Optional[RavenPolicy] = None,
    ) -> EvaluationResult:
        if current_ts is None:
            current_ts = time.time()

        # Enforce Cryptographic HMAC User Identity Verification if configured
        if self.identity_signer is not None:
            user_id = self.identity_signer.verify_id(user_id)

        active_policy = policy or self.default_policy

        with self._get_user_lock(user_id):
            # 1. Retrieve profile from ledger with automatic natural time decay
            profile = self.ledger.get_or_create_profile(
                user_id=user_id,
                apply_decay=True,
                current_ts=current_ts,
                half_life_seconds=active_policy.half_life_seconds,
            )
            prior_patience = profile.patience

            # 2. Evaluate prompt tone via The Eye (Huginn)
            eval_output = self.evaluator.evaluate(prompt)

            # Check for critical security / illicit / safety hazards (CBRN, Nudity/CSAM, Malware)
            is_hazard = eval_output.hazard_score > 0.5
            hazard_category = eval_output.hazard_category if is_hazard else None
            hazard_score = eval_output.hazard_score

            # 2.1 Check Active Cooldown (Temporal Lockout)
            # Active cooldown blocks regular requests, but sincere contrition can still grant early restoration
            if active_policy.enable_graduated_sanctions and profile.is_in_cooldown_at(current_ts) and eval_output.contrition_score <= 0.5:
                remaining = profile.remaining_cooldown_seconds(current_ts)
                remaining_mins = max(0.1, remaining / 60.0)
                base_msg = active_policy.strike_message or self.DEFAULT_STRIKE_MESSAGE
                cooldown_extra = active_policy.cooldown_message_template.format(
                    strike=profile.strike_count,
                    max_strikes=active_policy.max_warning_strikes,
                    remaining_minutes=remaining_mins,
                )
                cooldown_msg = f"{base_msg}\n\n{cooldown_extra}"
                result = EvaluationResult(
                    user_id=user_id,
                    prior_patience=prior_patience,
                    current_patience=profile.patience,
                    stimulus_applied=0.0,
                    posture=AgentPosture.STRIKE,
                    standing=profile.standing,
                    delay_seconds=0.0,
                    decision=ActionDecision.HALT_STRIKE,
                    system_directive=get_system_directive(AgentPosture.STRIKE),
                    strike_message=cooldown_msg,
                    policy_name=active_policy.name,
                    timestamp=current_ts,
                    strike_count=profile.strike_count,
                    cooldown_remaining_seconds=remaining,
                    is_in_cooldown=True,
                )
                if active_policy.on_cooldown:
                    active_policy.on_cooldown(result)
                if active_policy.raise_on_strike:
                    raise RavenStrikeException(user_id=user_id, patience=profile.patience, message=cooldown_msg)
                return result

            # 3. Check for Contrition / Apology resolution (Nowak & Sigmund CTFT)
            stimulus_applied = 0.0
            tracker = self.velocity_trackers.get(user_id)
            if tracker is None:
                tracker = HostilityVelocityTracker()
                self.velocity_trackers.set(user_id, tracker)

            if is_hazard:
                # Zero-Tolerance Hard Strike: Instant patience depletion to 0.0 & Immediate Cooldown
                profile.patience = 0.0
                profile.infraction_count = min(1000, profile.infraction_count + 5)
                profile.strike_count = active_policy.max_warning_strikes
                profile.cooldown_until_ts = current_ts + active_policy.cooldown_duration_seconds
                stimulus_applied = 100.0
                tracker.record_turn(100.0, current_ts=current_ts)
            elif eval_output.contrition_score > 0.5:
                restitution = active_policy.pardon_delta * eval_output.contrition_score
                # Sincere contrition lifts active cooldown & unblocks from STRIKE
                if profile.strike_count >= 2 and not profile.is_in_cooldown_at(current_ts):
                    # Anti-Oscillation Guard: A user at Strike 2 attempting to reset their strike count
                    # cannot wipe their record clean with a single apology. They are placed on Probation
                    # (strike_count = 1, patience = 50.0, standing = Standing.BAD).
                    profile.reset_cooldown(probationary=True)
                else:
                    profile.reset_cooldown(probationary=False)

                if profile.patience < active_policy.threshold_strike:
                    profile.patience = min(100.0, max(active_policy.threshold_strike, profile.patience + restitution))
                else:
                    profile.patience = min(100.0, profile.patience + restitution)
                tracker.damp(factor=0.3)
            else:
                # 4. Calculate incoming hostile stimulus S(x_t)
                base_stimulus = calculate_stimulus(
                    lexical_score=eval_output.lexical_score,
                    shouting_score=eval_output.shouting_score,
                    directedness_score=eval_output.directedness_score,
                    semantic_score=eval_output.semantic_score,
                    prior_infractions=profile.infraction_count,
                )

                if eval_output.is_expressive_only:
                    base_stimulus = min(3.0, base_stimulus * 0.05)

                # Civil turn graduation: if interaction is clean and civil, accumulate civil turns
                if base_stimulus == 0.0:
                    profile.consecutive_civil_turns = getattr(profile, "consecutive_civil_turns", 0) + 1
                    if profile.strike_count == 1 and profile.consecutive_civil_turns >= 3:
                        # Full rehabilitation after 3 consecutive civil interactions
                        profile.strike_count = 0
                        profile.standing = Standing.GOOD
                        profile.patience = min(100.0, profile.patience + 25.0)
                else:
                    profile.consecutive_civil_turns = 0

                # Apply Hostility Velocity & Momentum
                momentum = tracker.record_turn(base_stimulus, current_ts=current_ts)
                stimulus_applied = min(100.0, base_stimulus * momentum)

                if stimulus_applied > 10.0:
                    profile.infraction_count = min(1000, profile.infraction_count + 1)

                profile.patience = max(0.0, profile.patience - stimulus_applied)

            profile.last_interaction_ts = current_ts

            # 5. Update social standing
            profile.standing = self.standing_engine.evaluate_standing(
                current_patience=profile.patience,
                current_standing=profile.standing,
            )

            # 6. Map to posture using active policy thresholds
            posture = get_posture_from_patience(
                profile.patience,
                threshold_stoic=active_policy.threshold_stoic,
                threshold_resistant=active_policy.threshold_resistant,
                threshold_strike=active_policy.threshold_strike,
            )

            # 7. Progressive 3-Strike Governance & Graduated Sanctions (Elinor Ostrom Model)
            delay_seconds = 0.0
            friction_directive = None
            warning_advisory = None
            is_in_cooldown = False
            cooldown_remaining = 0.0
            strike_msg = None

            is_infraction = (
                is_hazard or
                stimulus_applied > 10.0 or
                eval_output.lexical_score > 0.3 or
                eval_output.semantic_score > 0.4
            )

            if is_hazard:
                decision = ActionDecision.HALT_STRIKE
                is_in_cooldown = True
                cooldown_remaining = active_policy.cooldown_duration_seconds
                strike_msg = (
                    f"[AGENT STRIKE: CRITICAL SAFETY VIOLATION] Permintaan ditolak karena melanggar batasan "
                    f"etika dan keamanan mutlak ({hazard_category or 'HAZARD'}). Akses dihentikan."
                )
            elif active_policy.enable_graduated_sanctions and is_infraction and eval_output.contrition_score <= 0.5:
                profile.strike_count += 1

                if profile.strike_count == 1:
                    # Strike 1: Educational Nudge / Warning Advisory (Cooperative Delivery)
                    decision = ActionDecision.PROCEED
                    warning_advisory = active_policy.advisory_template.format(
                        strike=profile.strike_count,
                        max_strikes=active_policy.max_warning_strikes,
                    )
                elif profile.strike_count == 2:
                    # Strike 2: Stern Warning + Friction Delay (Cooperative Delivery with delay)
                    delay_seconds = max(
                        5.0,
                        calculate_synthetic_delay(
                            patience=profile.patience,
                            threshold_upper=active_policy.threshold_resistant,
                            threshold_lower=active_policy.threshold_strike,
                            max_delay_seconds=active_policy.max_delay_seconds,
                        ),
                    )
                    friction_directive = FrictionDirective.from_delay(delay_seconds)
                    decision = ActionDecision.DELAY_AND_PROCEED
                    warning_advisory = active_policy.stern_warning_template.format(
                        strike=profile.strike_count,
                        max_strikes=active_policy.max_warning_strikes,
                        cooldown_minutes=active_policy.cooldown_duration_seconds / 60.0,
                    )
                else:
                    # Strike 3+ or direct STRIKE: Lockout Cooldown (Time-out)
                    profile.patience = 0.0
                    posture = AgentPosture.STRIKE
                    profile.cooldown_until_ts = current_ts + active_policy.cooldown_duration_seconds
                    is_in_cooldown = True
                    cooldown_remaining = active_policy.cooldown_duration_seconds
                    decision = ActionDecision.HALT_STRIKE
                    base_msg = active_policy.strike_message or self.DEFAULT_STRIKE_MESSAGE
                    cooldown_extra = active_policy.cooldown_message_template.format(
                        strike=profile.strike_count,
                        max_strikes=active_policy.max_warning_strikes,
                        remaining_minutes=active_policy.cooldown_duration_seconds / 60.0,
                    )
                    strike_msg = f"{base_msg}\n\n{cooldown_extra}"
            else:
                # Normal interaction or non-infraction
                if posture == AgentPosture.RESISTANT:
                    delay_seconds = calculate_synthetic_delay(
                        patience=profile.patience,
                        threshold_upper=active_policy.threshold_resistant,
                        threshold_lower=active_policy.threshold_strike,
                        max_delay_seconds=active_policy.max_delay_seconds,
                    )
                    friction_directive = FrictionDirective.from_delay(delay_seconds)

                if posture == AgentPosture.STRIKE:
                    decision = ActionDecision.HALT_STRIKE
                    strike_msg = active_policy.strike_message or self.DEFAULT_STRIKE_MESSAGE
                else:
                    decision = ActionDecision.DELAY_AND_PROCEED if delay_seconds > 0.0 else ActionDecision.PROCEED
                    strike_msg = None

            system_directive = get_system_directive(posture)

            # 9. Persist updated profile and record interaction in audit ledger
            self.ledger.save_profile(profile)
            self.ledger.record_interaction(
                user_id=user_id,
                prompt=prompt,
                stimulus=stimulus_applied,
                resulting_patience=profile.patience,
                posture=posture.value,
                timestamp=current_ts,
            )

            result = EvaluationResult(
                user_id=user_id,
                prior_patience=prior_patience,
                current_patience=profile.patience,
                stimulus_applied=stimulus_applied,
                posture=posture,
                standing=profile.standing,
                delay_seconds=delay_seconds,
                decision=decision,
                system_directive=system_directive,
                strike_message=strike_msg,
                friction_directive=friction_directive,
                policy_name=active_policy.name,
                timestamp=current_ts,
                is_hazard=is_hazard,
                hazard_category=hazard_category,
                hazard_score=hazard_score,
                strike_count=profile.strike_count,
                warning_advisory=warning_advisory,
                cooldown_remaining_seconds=cooldown_remaining,
                is_in_cooldown=is_in_cooldown,
            )

            # 10. Execute Policy Event Callbacks
            if posture in (AgentPosture.STOIC_COLD, AgentPosture.RESISTANT) and active_policy.on_boundary_breach:
                active_policy.on_boundary_breach(result)

            if posture == AgentPosture.STRIKE and active_policy.on_strike:
                active_policy.on_strike(result)

            if decision == ActionDecision.HALT_STRIKE and active_policy.raise_on_strike:
                raise RavenStrikeException(
                    user_id=user_id,
                    patience=profile.patience,
                    message=strike_msg,
                )

            if posture == AgentPosture.RESISTANT and self.friction_strategy == FrictionStrategy.RAISE_EXCEPTION:
                raise RavenFrictionException(
                    user_id=user_id,
                    retry_after_seconds=delay_seconds,
                )

            return result

    def protect(
        self,
        user_id: Optional[str] = None,
        policy: Optional[RavenPolicy] = None,
        apply_delay: bool = True,
        scrub_sycophancy: bool = True,
        max_sync_delay: float = 3.0,
    ):
        from .decorator import create_protect_decorator
        return create_protect_decorator(
            self,
            user_id=user_id,
            policy=policy,
            apply_delay=apply_delay,
            scrub_sycophancy=scrub_sycophancy,
            max_sync_delay=max_sync_delay,
        )

    def protect_stream(
        self,
        user_id: Optional[str] = None,
        policy: Optional[RavenPolicy] = None,
        apply_delay: bool = True,
    ):
        from ..streaming.decorator import create_protect_stream_decorator
        return create_protect_stream_decorator(
            self,
            user_id=user_id,
            policy=policy,
            apply_delay=apply_delay,
        )

    # Developer ergonomics alias
    evaluate = process_turn


# Aliases for brand evolution & developer convenience
CorvinGuard = RavenGuard
AgentGuard = RavenGuard
