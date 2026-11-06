"""
Ravens: A Cognitive Boundary & Grudge-Memory Engine for Sovereign AI Agents.
"""

from .core.state import AgentPosture, get_posture_from_patience, get_system_directive
from .core.standing import Standing, StandingEngine
from .core.models import UserPatienceProfile, EvaluationResult, ActionDecision
from .core.exceptions import RavenException, RavenStrikeException
from .evaluators.base import BaseEvaluator, ToneEvaluation
from .evaluators.heuristic import HuginnEye
from .evaluators.moderation import OpenAIModerationEvaluator
from .evaluators.hybrid import HybridEvaluator
from .storage.base import BaseLedger
from .storage.memory import InMemoryLedger
from .storage.sqlite import SQLiteLedger, with_sqlite_retry
from .storage.redis import RedisLedger
from .guard.core import RavenGuard
from .morphology.normalizer import MorphologyNormalizer
from .morphology.fuzzy import jaro_winkler_similarity
from .morphology.homoglyphs import fold_homoglyphs
from .morphology.zalgo import strip_zalgo
from .semantic.patterns import SemanticIntent
from .semantic.velocity import HostilityVelocityTracker
from .semantic.evaluator import SemanticEvaluator, SemanticEvaluation
from .policies.base import RavenPolicy
from .policies.presets import (
    create_free_tier_policy,
    create_enterprise_support_policy,
    create_gaming_npc_policy,
    create_security_sentinel_policy,
    create_progressive_cooldown_policy,
)
from .policies.notifier import InMemoryEventNotifier, RavenEventLog
from .streaming.interceptor import StreamInterceptor
from .scrubbers.stripper import SycophancyStripper
from .resilience.cache import BoundedTTLCache
from .resilience.locks import UserLockRegistry
from .resilience.friction import (
    FrictionStrategy,
    FrictionDirective,
    RavenFrictionException,
)
from .security.signer import (
    UserIdentitySigner,
    SecurityException,
    InvalidUserSignatureException,
)
from .integrations.fastapi import CorvinFastAPIMiddleware, CorvinRouteGuard
from .integrations.litellm import CorvinLLMInterceptor
from .integrations.langchain import CorvinCallbackHandler

# Corvin Aliases
CorvinGuard = RavenGuard
CorvinPolicy = RavenPolicy
CorvinException = RavenException
CorvinStrikeException = RavenStrikeException
RavenFastAPIMiddleware = CorvinFastAPIMiddleware
RavenRouteGuard = CorvinRouteGuard
RavenLLMInterceptor = CorvinLLMInterceptor
RavenCallbackHandler = CorvinCallbackHandler

__version__ = "0.8.4"

__all__ = [
    "CorvinGuard",
    "CorvinPolicy",
    "CorvinException",
    "CorvinStrikeException",
    "CorvinFastAPIMiddleware",
    "CorvinRouteGuard",
    "CorvinLLMInterceptor",
    "CorvinCallbackHandler",
    "RavenFastAPIMiddleware",
    "RavenRouteGuard",
    "RavenLLMInterceptor",
    "RavenCallbackHandler",
    "RavenGuard",
    "OpenAIModerationEvaluator",
    "HybridEvaluator",
    "AgentPosture",
    "get_posture_from_patience",
    "get_system_directive",
    "Standing",
    "StandingEngine",
    "UserPatienceProfile",
    "EvaluationResult",
    "ActionDecision",
    "RavenException",
    "RavenStrikeException",
    "BaseEvaluator",
    "ToneEvaluation",
    "HuginnEye",
    "BaseLedger",
    "InMemoryLedger",
    "SQLiteLedger",
    "RedisLedger",
    "with_sqlite_retry",
    "MorphologyNormalizer",
    "jaro_winkler_similarity",
    "fold_homoglyphs",
    "strip_zalgo",
    "SemanticIntent",
    "HostilityVelocityTracker",
    "SemanticEvaluator",
    "SemanticEvaluation",
    "RavenPolicy",
    "create_free_tier_policy",
    "create_enterprise_support_policy",
    "create_gaming_npc_policy",
    "create_security_sentinel_policy",
    "create_progressive_cooldown_policy",
    "InMemoryEventNotifier",
    "RavenEventLog",
    "StreamInterceptor",
    "SycophancyStripper",
    "BoundedTTLCache",
    "UserLockRegistry",
    "FrictionStrategy",
    "FrictionDirective",
    "RavenFrictionException",
    "UserIdentitySigner",
    "SecurityException",
    "InvalidUserSignatureException",
]
