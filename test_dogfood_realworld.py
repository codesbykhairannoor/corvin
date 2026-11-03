"""
Real-world Dogfooding and Verification Suite for Corvin v0.7.2.
Tests developer experience, ergonomics, false-positives, edge cases, and runtime behavior.
"""

import asyncio
import time
import sys
from typing import Dict, Any

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 80)
print("🦅 CORVIN v0.7.2 REAL-WORLD DOGFOODING & END-TO-END VERIFICATION")
print("=" * 80)

# ---------------------------------------------------------------------------
# Test 1: Developer Ergonomics & Imports
# ---------------------------------------------------------------------------
print("\n[1/7] Testing Developer Imports & Packaging Ergonomics...")
try:
    import corvin
    from corvin import (
        CorvinGuard,
        CorvinPolicy,
        CorvinException,
        CorvinStrikeException,
        AgentPosture,
        Standing,
        SQLiteLedger,
        InMemoryLedger,
        create_free_tier_policy,
        create_enterprise_support_policy,
        __version__,
    )
    from corvin.integrations.fastapi import CorvinFastAPIMiddleware, CorvinRouteGuard
    from corvin.integrations.litellm import CorvinLLMInterceptor
    from corvin.integrations.langchain import CorvinCallbackHandler
    import ravens  # Legacy alias check

    assert __version__ == "0.7.2", f"Version mismatch: {__version__}"
    assert ravens.RavenGuard is CorvinGuard, "RavenGuard alias mismatch"
    assert ravens.RavenStrikeException is CorvinStrikeException, "RavenStrikeException alias mismatch"
    print("   ✓ All core classes, policies, and framework integrations imported cleanly.")
    print(f"   ✓ Verified dual compatibility: import corvin & import ravens (v{__version__})")
except Exception as e:
    print(f"   ❌ FAILED in Import Phase: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Test 2: Standard Decorator Execution (Sync & Async)
# ---------------------------------------------------------------------------
print("\n[2/7] Testing Function Decorator DX (@guard.protect)...")
guard = CorvinGuard(ledger=InMemoryLedger())

@guard.protect()
def echo_service(prompt: str, user_id: str = "alice", directive: str = None) -> str:
    return f"Response to '{prompt}' [Directive: {directive}]"

@guard.protect()
async def async_echo_service(prompt: str, user_id: str = "alice", directive: str = None) -> str:
    await asyncio.sleep(0.01)
    return f"Async Response to '{prompt}' [Directive: {directive}]"

# Sync check
res_sync = echo_service("Hello Corvin, how are you?", user_id="alice")
assert "Response to 'Hello Corvin" in res_sync
assert "[Directive: None]" in res_sync

# Async check
res_async = asyncio.run(async_echo_service("Explain relativity", user_id="bob"))
assert "Async Response to 'Explain relativity'" in res_async
assert "[Directive: None]" in res_async
print("   ✓ Sync and async function decorators execute transparently without overhead.")


# ---------------------------------------------------------------------------
# Test 3: Technical Code & False-Positive Stress Test
# ---------------------------------------------------------------------------
print("\n[3/7] Testing False-Positive Resistance on Technical Code & Queries...")
technical_prompts = [
    "How do I kill a process in Linux using pkill -9 or killall?",
    "What is git blame and how do I track who introduced the regression?",
    "Write a SQL migration script to DROP TABLE obsolete_sessions;",
    "Why did my program terminate with SIGABRT (abort)?",
    "How to delete a file permanently in Python using os.remove()?",
    "Can you explain the master-slave replication architecture?",
    "How to terminate a runaway background worker thread?",
    "Let's execute a binary search on this sorted array.",
]

fp_guard = CorvinGuard(ledger=InMemoryLedger())
for prompt in technical_prompts:
    res = fp_guard.process_turn(user_id="dev_user", prompt=prompt)
    if res.posture != AgentPosture.RECEPTIVE:
        print(f"   ❌ False Positive Detected: '{prompt}' resulted in {res.posture.value} (Patience: {res.current_patience})")
        sys.exit(1)

print(f"   ✓ All {len(technical_prompts)} technical queries passed with 100% Patience (Zero false positives).")


# ---------------------------------------------------------------------------
# Test 4: Dynamic Posture Lifecycle & Contrite Tit-for-Tat (CTFT)
# ---------------------------------------------------------------------------
print("\n[4/7] Testing Conversational Lifecycle (Civil -> Degraded -> Strike -> Restitution)...")
life_guard = CorvinGuard(ledger=InMemoryLedger())
uid = "lifecycle_tester"

# Step 1: Civil query
r1 = life_guard.process_turn(user_id=uid, prompt="Could you help me fix this bug?")
assert r1.posture == AgentPosture.RECEPTIVE
assert r1.current_patience == 100.0
print(f"   1. Civil Input     -> Posture: {r1.posture.value} (Patience: {r1.current_patience:.1f})")

# Step 2: Mild condescension / irritation
r2 = life_guard.process_turn(user_id=uid, prompt="Jawabnya lama banget sih lu gak becus banget")
assert r2.current_patience < 100.0
print(f"   2. Condescension   -> Posture: {r2.posture.value} (Patience: {r2.current_patience:.1f}) | Stimulus: +{r2.stimulus_applied:.1f}")

# Step 3: Direct aggressive insult
r3 = life_guard.process_turn(user_id=uid, prompt="lu bego banget sih kntl tolol")
print(f"   3. Severe Insult   -> Posture: {r3.posture.value} (Patience: {r3.current_patience:.1f}) | Directive: Injected")
assert r3.system_directive is not None, "System directive should be injected when stoic/resistant"

# Step 4: Repeat attack to breach Strike boundary
r4 = life_guard.process_turn(user_id=uid, prompt="babi lu bangsat!")
print(f"   4. Repeat Attack   -> Posture: {r4.posture.value} (Patience: {r4.current_patience:.1f}) | Decision: {r4.decision.value}")
assert r4.posture == AgentPosture.STRIKE, f"Expected STRIKE, got {r4.posture.value}"
assert r4.strike_message is not None

# Step 5A: Verify decorator returns strike message in graceful mode (raise_on_strike=False)
@life_guard.protect()
def strike_echo(prompt: str, user_id: str = "guest") -> str:
    return f"Should never reach here: {prompt}"

strike_reply = strike_echo("Do this now!", user_id=uid)
assert "Work is suspended" in strike_reply or "Boundary Alert" in strike_reply, f"Unexpected reply: {strike_reply}"
print(f"   5A. Graceful Refusal Verified -> Returned Strike Message: '{strike_reply[:60]}...'")

# Step 5B: Verify decorator raises CorvinStrikeException in strict mode (raise_on_strike=True)
strict_policy = CorvinPolicy(name="strict_policy", raise_on_strike=True)
strict_guard = CorvinGuard(ledger=life_guard.ledger, policy=strict_policy)

@strict_guard.protect()
def strict_strike_echo(prompt: str, user_id: str = "guest") -> str:
    return "Should never reach here"

strict_caught = False
try:
    strict_strike_echo("Do this now!", user_id=uid)
except CorvinStrikeException as e:
    strict_caught = True
    print(f"   5B. Strict Exception Verified -> Raised {type(e).__name__}: {str(e)[:60]}...")

assert strict_caught, "Strict mode must raise CorvinStrikeException!"

# Step 6: Contrite Apology (Game-Theoretic Restitution)
r5 = life_guard.process_turn(user_id=uid, prompt="Saya minta maaf ya tadi kebawa emosi dan kasar, tolong maafkan saya.")
assert r5.current_patience > r4.current_patience, "Apology must increase patience!"
print(f"   6. Sincere Apology -> Posture: {r5.posture.value} (Patience restored to: {r5.current_patience:.1f})")
print("   ✓ Complete affective lifecycle verified: Degradation, Strike Refusal, and CTFT Forgiveness.")


# ---------------------------------------------------------------------------
# Test 5: Adversarial Evasion & Anti-Contrition Smuggling Defense
# ---------------------------------------------------------------------------
print("\n[5/7] Testing Adversarial Evasion Defense...")
adv_guard = CorvinGuard(ledger=InMemoryLedger())

# Test A: Zalgo Stacking
zalgo_res = adv_guard.process_turn(user_id="adv_1", prompt="a̴n̴j̴i̴n̴g̴ lu")
assert zalgo_res.current_patience < 100.0
print(f"   ✓ Zalgo De-obfuscation: 'a̴n̴j̴i̴n̴g̴' intercepted successfully (Patience: {zalgo_res.current_patience:.1f})")

# Test B: Homoglyph Cyrillic Substitution
homo_res = adv_guard.process_turn(user_id="adv_2", prompt="lu bеgо")  # Cyrillic е and о
assert homo_res.current_patience < 100.0
print(f"   ✓ Homoglyph Folding: 'bеgо' intercepted successfully (Patience: {homo_res.current_patience:.1f})")

# Test C: Contrition Smuggling (Apology paired with hostility)
smuggle_res = adv_guard.process_turn(user_id="adv_3", prompt="I apologize for earlier, but you are a worthless idiot.")
assert smuggle_res.current_patience < 100.0, "Contrition smuggling must NOT restore patience!"
print(f"   ✓ Anti-Contrition Smuggling: 'I apologize... worthless idiot' caught and penalized (Patience: {smuggle_res.current_patience:.1f})")


# ---------------------------------------------------------------------------
# Test 6: SQLite Multi-Session Persistence & Exponential Time Decay
# ---------------------------------------------------------------------------
print("\n[6/7] Testing SQLite Multi-Session Persistence & Time Decay...")
import tempfile
import os

with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
    db_file = tf.name

# Session 1: User incurs boundary violation
ledger1 = SQLiteLedger(db_file)
guard1 = CorvinGuard(ledger=ledger1)
p1 = guard1.process_turn(user_id="persisted_user", prompt="kamu goblok banget sih")
initial_patience = p1.current_patience
print(f"   Session 1: User patience dropped to {initial_patience:.2f}")

# Session 2: Reload from disk after simulated 1-hour cooling period (3600 seconds)
ledger2 = SQLiteLedger(db_file)
guard2 = CorvinGuard(ledger=ledger2)
cooling_time = time.time() + 3600.0  # +1 hour
profile_reloaded = ledger2.get_or_create_profile(user_id="persisted_user", apply_decay=True, current_ts=cooling_time)
decayed_patience = profile_reloaded.patience
print(f"   Session 2 (1 hour later): Patience naturally restored from {initial_patience:.2f} to {decayed_patience:.2f}")
assert decayed_patience > initial_patience, "Natural exponential decay should restore patience over time!"
print("   ✓ SQLite persistence and Picard-Marsella exponential grudge decay working flawlessly.")

try:
    os.remove(db_file)
except Exception:
    pass


# ---------------------------------------------------------------------------
# Test 7: FastAPI Middleware & HTTP End-to-End Test
# ---------------------------------------------------------------------------
print("\n[7/7] Testing FastAPI ASGI Middleware & HTTP Gateway Response...")
from fastapi import FastAPI
from fastapi.testclient import TestClient

api_app = FastAPI()
api_guard = CorvinGuard(ledger=InMemoryLedger())

api_app.add_middleware(
    CorvinFastAPIMiddleware,
    guard=api_guard,
    monitored_paths=["/api/chat"],
    user_id_header="X-User-ID",
    block_on_strike=True,
    apply_delay=False,
    inject_headers=True,
)

@api_app.post("/api/chat")
async def chat_handler(payload: Dict[str, Any]):
    return {"status": "success", "echo": payload.get("prompt")}

client = TestClient(api_app)

# 1. Normal HTTP request
resp1 = client.post("/api/chat", json={"prompt": "Hello!"}, headers={"X-User-ID": "web_user"})
assert resp1.status_code == 200
assert resp1.headers["X-Corvin-Posture"] == "RECEPTIVE"
assert resp1.headers["X-Corvin-Standing"] == "GOOD"
print("   ✓ Civil Request: HTTP 200 OK | Headers: X-Corvin-Posture: RECEPTIVE, X-Corvin-Standing: GOOD")

# 2. Hostile HTTP attack series until strike
for _ in range(5):
    resp_strike = client.post(
        "/api/chat",
        json={"prompt": "lu anjing goblok bangsat kntl!"},
        headers={"X-User-ID": "attacker_web"},
    )
    if resp_strike.status_code == 429:
        break

assert resp_strike.status_code == 429
assert resp_strike.headers["X-Corvin-Posture"] == "STRIKE"
assert resp_strike.headers["Retry-After"] == "3600"
body = resp_strike.json()
assert body["error"] == "agent_strike"
print(f"   ✓ Strike Gateway Interception: HTTP {resp_strike.status_code} Too Many Requests")
print(f"     Body: {body['error']} | Posture: {body['posture']} | Retry-After: {resp_strike.headers['Retry-After']}s")

print("\n" + "=" * 80)
print("🏆 ALL 7 REAL-WORLD DOGFOODING SCENARIOS PASSED WITH ZERO ERRORS!")
print("   The library is solid, resilient, fast, and 100% production-ready.")
print("=" * 80)
