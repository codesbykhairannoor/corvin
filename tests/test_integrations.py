import pytest
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient

from corvin import CorvinGuard, AgentPosture, Standing, RavenStrikeException
from corvin.integrations.fastapi import CorvinFastAPIMiddleware, CorvinRouteGuard
from corvin.integrations.litellm import CorvinLLMInterceptor
from corvin.integrations.langchain import CorvinCallbackHandler
from corvin.storage.memory import InMemoryLedger


def create_test_app():
    app = FastAPI()
    guard = CorvinGuard(ledger=InMemoryLedger())

    app.add_middleware(
        CorvinFastAPIMiddleware,
        guard=guard,
        monitored_paths=["/chat", "/api/v1/chat"],
        user_id_header="X-User-ID",
        block_on_strike=True,
        apply_delay=False,  # Keep tests fast
        inject_headers=True,
    )

    @app.post("/chat")
    async def chat_endpoint(request: Request):
        body = await request.json()
        corvin_res = getattr(request.state, "corvin_result", None)
        directive = corvin_res.system_directive if corvin_res else None
        return {
            "reply": f"Response to: {body.get('prompt')}",
            "directive": directive,
        }

    route_guard = CorvinRouteGuard(guard=guard)

    @app.post("/guarded-route")
    async def guarded_route(request: Request, eval_res=Depends(route_guard)):
        return {
            "user_id": eval_res.user_id,
            "posture": eval_res.posture.value,
            "patience": eval_res.current_patience,
        }

    return app, guard


def test_fastapi_middleware_civil_request():
    app, guard = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"prompt": "Hello! Could you help me with a Python script?"},
        headers={"X-User-ID": "alice"},
    )
    assert response.status_code == 200
    assert response.headers["X-Corvin-Posture"] == "RECEPTIVE"
    assert float(response.headers["X-Corvin-Patience"]) == 100.0
    data = response.json()
    assert "Response to: Hello!" in data["reply"]
    assert data["directive"] is None


def test_fastapi_middleware_hostile_strike():
    app, guard = create_test_app()
    client = TestClient(app)

    # Attack user_bad until strike occurs
    for _ in range(5):
        resp = client.post(
            "/chat",
            json={"prompt": "kamu anjing goblok banget sih bangsat tolol"},
            headers={"X-User-ID": "bad_actor"},
        )
        if resp.status_code == 429:
            break

    assert resp.status_code == 429
    assert resp.headers["X-Corvin-Posture"] == "STRIKE"
    body = resp.json()
    assert body["error"] == "agent_strike"
    assert "Work is suspended" in body["detail"]
    assert body["posture"] == "STRIKE"


def test_fastapi_middleware_openai_message_format():
    app, guard = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": "Please explain recursion."},
            ]
        },
        headers={"X-User-ID": "bob"},
    )
    assert response.status_code == 200
    assert response.headers["X-Corvin-Posture"] == "RECEPTIVE"


def test_fastapi_route_guard_dependency():
    app, guard = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/guarded-route",
        json={"prompt": "Good morning assistant!"},
        headers={"X-User-ID": "charlie"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "charlie"
    assert data["posture"] == "RECEPTIVE"
    assert data["patience"] == 100.0


def test_litellm_interceptor_prepare_messages():
    guard = CorvinGuard(ledger=InMemoryLedger())
    interceptor = CorvinLLMInterceptor(guard=guard)

    messages = [
        {"role": "system", "content": "Base prompt."},
        {"role": "user", "content": "kamu goblok banget sih"},
    ]

    new_messages, result = interceptor.prepare_messages(messages, user_id="litellm_user")
    assert result.current_patience < 100.0
    assert len(new_messages) == 2
    # System prompt should be augmented with directive
    assert "RAVENS_DIRECTIVE" in new_messages[0]["content"]


def test_litellm_interceptor_sycophancy_stripping():
    guard = CorvinGuard(ledger=InMemoryLedger())
    interceptor = CorvinLLMInterceptor(guard=guard)

    sycophantic_output = "I'm so sorry! As an AI language model, I apologize. The answer is 42."
    stripped = interceptor.process_response(sycophantic_output)
    assert "I'm so sorry" not in stripped
    assert "apologize" not in stripped
    assert stripped == "The answer is 42."


def test_langchain_callback_handler():
    guard = CorvinGuard(ledger=InMemoryLedger())
    handler = CorvinCallbackHandler(guard=guard, default_user_id="lc_user")

    # Civil prompt
    handler.on_llm_start(
        serialized={},
        prompts=["How does quicksort work?"],
    )
    profile = guard.ledger.get_or_create_profile("lc_user")
    assert profile.patience == 100.0

    # Hostile prompts triggering strike
    with pytest.raises(RavenStrikeException):
        for _ in range(5):
            handler.on_llm_start(
                serialized={},
                prompts=["kamu anjing goblok banget sih bangsat tolol"],
            )
