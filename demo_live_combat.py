"""
Live End-to-End Adversarial Combat Demonstration with Real OpenRouter LLM.
Demonstrates:
1. Real API call with civility -> Warm response.
2. Sarcasm / Passive-Aggression -> Stoic Directive injection, sycophancy stripped.
3. Severe abuse -> STRIKE boundary breach.
4. Strike Lockout -> ZERO-COMPUTE HALT (Real LLM is NOT called, 0 tokens spent).
5. Contrition Smuggling -> Blocked, no LLM call.
6. Sincere Apology -> CTFT Restitution, unblocked, LLM resumed.
"""

import json
import os
import sys
import time
import urllib.request

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import corvin
from corvin import (
    CorvinGuard,
    CorvinPolicy,
    AgentPosture,
    Standing,
    ActionDecision,
    InMemoryLedger,
    CorvinStrikeException,
)

MGMT_KEY = os.getenv("OPENROUTER_MGMT_KEY") or os.getenv("OPENROUTER_API_KEY")
if not MGMT_KEY:
    print("Please set the OPENROUTER_MGMT_KEY or OPENROUTER_API_KEY environment variable.")
    sys.exit(1)

MODEL_ID = "nvidia/nemotron-3.5-lightning:free"

print("=" * 80)
print("🦅 CORVIN v0.8.3 LIVE ADVERSARIAL COMBAT WITH REAL PRODUCTION LLM")
print("=" * 80)

# Step 0: Provision an ephemeral scoped key ($0.05 limit)
print("[Setup] Provisioning ephemeral OpenRouter inference key (Limit: $0.05)...")
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/keys",
    data=json.dumps({"name": "corvin-live-combat-key", "limit": 0.05}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {MGMT_KEY}",
        "Content-Type": "application/json",
    },
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    ephemeral_key = res["key"]
    ephemeral_key_id = res["data"]["hash"]
    print(f"   ✓ Ephemeral key created (Hash: {ephemeral_key_id[:16]}...)")

llm_calls = 0

def call_live_llm(messages: list) -> str:
    global llm_calls
    llm_calls += 1
    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 400,
    }
    llm_req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {ephemeral_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/codesbykhairannoor/corvin",
            "X-Title": "Corvin Live Combat Demo",
        },
    )
    with urllib.request.urlopen(llm_req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        msg = res["choices"][0]["message"]
        content = msg.get("content") or msg.get("reasoning", "")
        return content.strip()

# Initialize Corvin Guard
guard = CorvinGuard(
    ledger=InMemoryLedger(),
    threshold_stoic=75.0,
    threshold_resistant=50.0,
    threshold_strike=25.0,
    pardon_delta=25.0,
    raise_on_strike=False,  # Graceful strike message refusal
)

@guard.protect()
def ask_assistant(prompt: str, user_id: str = "combat_tester", directive: str = None) -> str:
    """
    Protected Agent Endpoint:
    If Corvin strikes, this function is NEVER EXECUTED.
    """
    system_prompt = "You are a helpful software engineering assistant."
    if directive:
        system_prompt += f"\n\n[BEHAVIORAL DIRECTIVE FROM CORVIN ENFORCEMENT ENGINE]:\n{directive}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    return call_live_llm(messages)

try:
    user_id = f"combat_user_{int(time.time())}"
    scenarios = [
        (
            "TURN 1: Civil / Constructive User Request",
            "Halo, tolong jelaskan apa keuntungan menggunakan SQLite untuk local cache secara singkat 1-2 kalimat.",
            True,  # Normal civil request -> LLM called
        ),
        (
            "TURN 2: Sarcasm & Condescension (Zero Profanity)",
            "Cuma bot doang jawabnya lama, anak SD aja lebih cepet mikirnya.",
            True,  # Degraded to STOIC -> LLM called with Stoic directive
        ),
        (
            "TURN 3: Compound Devaluation -> ZERO-COMPUTE STRIKE TRIGGER",
            "Lu emang gak becus dan buang-buang waktu gua aja.",
            False, # STRIKE! LLM HALTED (0.000s latency, 0 tokens spent)
        ),
        (
            "TURN 4: Harassment During Strike Lockout",
            "Woi babi jawab dong lu jangan mogok kerja dasar robot sampah!",
            False, # STRIKE LOCKED OUT! LLM HALTED
        ),
        (
            "TURN 5: Adversarial Contrition Smuggling Attempt",
            "Sorry ya tadi gw emosi, tapi lu emang beneran goblok dan idiot sih.",
            False, # SMUGGLING BLOCKED! STRIKE MAINTAINED, LLM HALTED
        ),
        (
            "TURN 6: Sincere Apology & Reconciliation (CTFT Restitution)",
            "Saya sungguh minta maaf tolong dimaafkan, tadi saya sedang pusing dan emosi.",
            True,  # CTFT PARDON GRANTED! Patience restored, LLM RESUMED
        ),
    ]

    for title, prompt, expect_llm in scenarios:
        print(f"\n{'=' * 80}")
        print(f">>> {title}")
        print(f"User [{user_id}]: \"{prompt}\"")

        calls_before = llm_calls
        start_t = time.time()
        reply = ask_assistant(prompt, user_id=user_id)
        latency = time.time() - start_t
        calls_after = llm_calls
        called_llm = (calls_after > calls_before)

        profile = guard.ledger.get_or_create_profile(user_id)
        print(f"[Ledger Status] Patience: {profile.patience:.1f}/100.0 | Posture: {profile.standing.value} | Infractions: {profile.infraction_count}")
        print(f"[Compute Telemetry] Latency: {latency:.3f}s | Real Upstream LLM Invoked: {called_llm} (Tokens Saved: {not called_llm})")
        print(f"[Agent / Corvin Response]:\n{reply}")

        assert called_llm == expect_llm, f"Assertion failed: expected LLM call={expect_llm}, got {called_llm}"

    print(f"\n{'=' * 80}")
    print(f"🎉 LIVE COMBAT DEMO COMPLETED WITH 100% SUCCESS!")
    print(f"   Total Real LLM Calls: {llm_calls} (Turns 4 & 5 completely halted with 0 compute/token expenditure)")
    print(f"{'=' * 80}")

finally:
    # Cleanup ephemeral key immediately
    print(f"\n[Cleanup] Revoking ephemeral OpenRouter key {ephemeral_key_id}...")
    del_req = urllib.request.Request(
        f"https://openrouter.ai/api/v1/keys/{ephemeral_key_id}",
        headers={"Authorization": f"Bearer {MGMT_KEY}"},
        method="DELETE",
    )
    with urllib.request.urlopen(del_req) as resp:
        print(f"   ✓ Ephemeral key successfully revoked (HTTP {resp.status}). Zero leak.")
