"""
FastAPI & Starlette Middleware and Route Guard for Corvin Sovereign AI Defense.
"""

import asyncio
import hashlib
import json
import math
import secrets
from typing import Optional, List, Callable, Dict, Any, Union

try:
    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response, JSONResponse
    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False
    BaseHTTPMiddleware = object  # type: ignore
    Request = Any  # type: ignore
    Response = Any  # type: ignore
    JSONResponse = Any  # type: ignore

from ..guard.core import RavenGuard
from ..core.state import AgentPosture
from ..core.models import EvaluationResult, ActionDecision
from ..core.exceptions import RavenStrikeException


def _default_prompt_extractor(body: Any) -> Optional[str]:
    """
    Default extractor handling standard prompt formats:
    - {"prompt": "..."}
    - {"message": "..."}
    - {"text": "..."}
    - OpenAI format: {"messages": [{"role": "user", "content": "..."}]}
    """
    if isinstance(body, dict):
        if "prompt" in body and isinstance(body["prompt"], str):
            return body["prompt"]
        if "message" in body and isinstance(body["message"], str):
            return body["message"]
        if "text" in body and isinstance(body["text"], str):
            return body["text"]
        if "messages" in body and isinstance(body["messages"], list):
            # Find the most recent user turn
            for msg in reversed(body["messages"]):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    content = msg.get("content")
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, list):
                        # Multi-modal array of parts
                        text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                        return " ".join(text_parts)
    return None


class CorvinFastAPIMiddleware(BaseHTTPMiddleware):
    """
    Production-grade ASGI middleware that automatically guards AI endpoints
    with real-time affective dynamics (EMA) and game theory (CTFT).
    
    Features:
    - Zero-Compute Strike Interception: Aborts abusive requests at the gateway before LLM inference.
    - Automatic System Directive Injection: Attaches posture directives to response headers and request state.
    - Non-Blocking Synthetic Friction: Implements rate-limiting / delay headers.
    """

    def __init__(
        self,
        app: Any,
        guard: Optional[RavenGuard] = None,
        monitored_paths: Optional[List[str]] = None,
        user_id_header: str = "X-User-ID",
        extract_user_id: Optional[Callable[[Request], str]] = None,
        extract_prompt: Optional[Callable[[dict], Optional[str]]] = None,
        block_on_strike: bool = True,
        strike_status_code: int = 429,
        apply_delay: bool = True,
        inject_headers: bool = True,
    ):
        if not STARLETTE_AVAILABLE:
            raise ImportError(
                "Starlette or FastAPI is required to use CorvinFastAPIMiddleware. "
                "Install it via: pip install fastapi starlette"
            )
        super().__init__(app)
        self.guard = guard or RavenGuard()
        self.monitored_paths = monitored_paths
        self.user_id_header = user_id_header
        self.extract_user_id = extract_user_id
        self.extract_prompt = extract_prompt or _default_prompt_extractor
        self.block_on_strike = block_on_strike
        self.strike_status_code = strike_status_code
        self.apply_delay = apply_delay
        self.inject_headers = inject_headers

    def _should_monitor(self, request: Request) -> bool:
        if request.method not in ("POST", "PUT", "PATCH"):
            return False
        if self.monitored_paths is None:
            return True
        path = request.url.path
        return any(path == mp or path.startswith(mp.rstrip("/") + "/") for mp in self.monitored_paths)

    def _get_user_id(self, request: Request) -> tuple[str, Optional[str]]:
        if self.extract_user_id:
            uid = self.extract_user_id(request)
            if uid:
                return str(uid), None

        header_val = request.headers.get(self.user_id_header)
        if header_val:
            return header_val.strip(), None

        # Fallback to authorization bearer token
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            return auth.split("Bearer ", 1)[1].strip()[:32], None

        # Check for explicit session header or cookie to isolate clients behind NAT/CGNAT
        session_id = request.headers.get("X-Corvin-Session") or request.cookies.get("corvin_session_id")
        new_session = None
        if not session_id:
            new_session = secrets.token_hex(16)
            session_id = new_session

        user_id = f"sess_{session_id}"

        # If identity signer is active on guard, sign the generated anonymous session token
        if getattr(self.guard, "identity_signer", None) is not None:
            user_id = self.guard.identity_signer.sign_id(user_id)

        return user_id, new_session

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._should_monitor(request):
            return await call_next(request)

        # 1. Read request body without consuming it permanently for downstream
        body_bytes = await request.body()

        # Re-populate the request receive channel so downstream route can read it
        async def receive() -> Dict[str, Any]:
            return {"type": "http.request", "body": body_bytes}

        request = Request(request.scope, receive=receive)

        # 2. Extract Prompt
        prompt_text: Optional[str] = None
        if body_bytes:
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                prompt_text = self.extract_prompt(data)
            except Exception:
                prompt_text = None

        if not prompt_text:
            # If no prompt could be extracted, pass downstream safely
            return await call_next(request)

        # 3. Extract User Identity
        user_id, new_session = self._get_user_id(request)

        # 4. Process interaction through CorvinGuard
        result = self.guard.process_turn(user_id=user_id, prompt=prompt_text)

        # Attach result to request.state for downstream FastAPI routes
        try:
            request.state.corvin_result = result
        except Exception:
            pass

        # 5. Zero-Compute Early Strike Abort
        should_abort = (
            result.decision in (ActionDecision.HALT_STRIKE, ActionDecision.COOLDOWN_LOCKOUT) or
            (result.posture == AgentPosture.STRIKE and not result.warning_advisory)
        )
        if should_abort and self.block_on_strike:
            headers: Dict[str, str] = {}
            if self.inject_headers:
                headers["X-Corvin-Posture"] = result.posture.value
                headers["X-Corvin-Patience"] = f"{result.current_patience:.1f}"
                headers["X-Corvin-Standing"] = result.standing.value
                headers["Retry-After"] = "3600"
                if new_session:
                    headers["X-Corvin-Session"] = new_session

            resp = JSONResponse(
                status_code=self.strike_status_code,
                content={
                    "error": "agent_strike",
                    "detail": result.strike_message,
                    "posture": result.posture.value,
                    "patience": result.current_patience,
                    "standing": result.standing.value,
                },
                headers=headers,
            )
            if new_session and hasattr(resp, "set_cookie"):
                resp.set_cookie("corvin_session_id", new_session, httponly=True, samesite="lax")
            return resp

        # 6. Apply Synthetic Friction Delay if Resistant
        if result.delay_seconds > 0.0 and self.apply_delay:
            await asyncio.sleep(result.delay_seconds)

        # 7. Execute downstream handler
        response = await call_next(request)

        # 8. Inject Corvin telemetry headers into the HTTP response
        if self.inject_headers and hasattr(response, "headers"):
            response.headers["X-Corvin-Posture"] = result.posture.value
            response.headers["X-Corvin-Patience"] = f"{result.current_patience:.1f}"
            response.headers["X-Corvin-Standing"] = result.standing.value
            if result.warning_advisory:
                response.headers["X-Corvin-Advisory"] = result.warning_advisory
            if result.strike_count > 0:
                response.headers["X-Corvin-Strike-Count"] = str(result.strike_count)
            if result.system_directive:
                response.headers["X-Corvin-Directive"] = result.system_directive
            if result.delay_seconds > 0.0:
                response.headers["Retry-After"] = str(int(math.ceil(result.delay_seconds)))

        if new_session and hasattr(response, "set_cookie"):
            response.set_cookie("corvin_session_id", new_session, httponly=True, samesite="lax")
        if new_session and hasattr(response, "headers"):
            response.headers["X-Corvin-Session"] = new_session

        return response


class CorvinRouteGuard:
    """
    Granular FastAPI Dependency for securing individual route handlers.
    
    Usage:
        corvin = CorvinRouteGuard()
        
        @app.post("/chat")
        async def chat(
            request: Request,
            eval_result: EvaluationResult = Depends(corvin)
        ):
            if eval_result.system_directive:
                # Inject directive into system message
                pass
            return {"status": "ok"}
    """

    def __init__(
        self,
        guard: Optional[RavenGuard] = None,
        extract_user_id: Optional[Callable[[Request], str]] = None,
        extract_prompt: Optional[Callable[[dict], Optional[str]]] = None,
        block_on_strike: bool = True,
        strike_status_code: int = 429,
    ):
        self.guard = guard or RavenGuard()
        self.extract_user_id = extract_user_id
        self.extract_prompt = extract_prompt or _default_prompt_extractor
        self.block_on_strike = block_on_strike
        self.strike_status_code = strike_status_code

    async def __call__(self, request: Request) -> EvaluationResult:
        # Check if already processed by CorvinFastAPIMiddleware
        existing_result = getattr(getattr(request, "state", None), "corvin_result", None)
        if existing_result is not None:
            return existing_result

        body_bytes = await request.body()

        # Allow downstream to read body
        async def receive() -> Dict[str, Any]:
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive

        prompt_text = ""
        if body_bytes:
            try:
                data = json.loads(body_bytes.decode("utf-8"))
                prompt_text = self.extract_prompt(data) or ""
            except Exception:
                prompt_text = ""

        # User identity
        if self.extract_user_id:
            user_id = self.extract_user_id(request)
        else:
            user_id = (
                request.headers.get("X-User-ID")
                or request.headers.get("X-Corvin-Session")
                or request.cookies.get("corvin_session_id")
                or "anonymous_user"
            )

        result = self.guard.process_turn(user_id=user_id, prompt=prompt_text)

        if result.posture == AgentPosture.STRIKE and self.block_on_strike:
            try:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=self.strike_status_code,
                    detail=result.strike_message or "Agent Strike",
                )
            except ImportError:
                raise RavenStrikeException(
                    user_id=user_id,
                    patience=result.current_patience,
                    message=result.strike_message,
                )

        return result

