"""
Ravens Framework Integrations (Alias for Corvin Integrations).
"""

from corvin.integrations.fastapi import CorvinFastAPIMiddleware as RavenFastAPIMiddleware, CorvinRouteGuard as RavenRouteGuard
from corvin.integrations.litellm import CorvinLLMInterceptor as RavenLLMInterceptor
from corvin.integrations.langchain import CorvinCallbackHandler as RavenCallbackHandler

# Aliases
CorvinFastAPIMiddleware = RavenFastAPIMiddleware
CorvinRouteGuard = RavenRouteGuard
CorvinLLMInterceptor = RavenLLMInterceptor
CorvinCallbackHandler = RavenCallbackHandler

__all__ = [
    "RavenFastAPIMiddleware",
    "RavenRouteGuard",
    "RavenLLMInterceptor",
    "RavenCallbackHandler",
    "CorvinFastAPIMiddleware",
    "CorvinRouteGuard",
    "CorvinLLMInterceptor",
    "CorvinCallbackHandler",
]

