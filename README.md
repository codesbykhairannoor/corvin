<p align="center">
  <img alt="Ravens Logo" src="assets/Ravens.png" width="220" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
</p>

<h1 align="center">ravens</h1>

<p align="center">
  <b>A Cognitive Boundary &amp; Grudge-Memory Engine for Sovereign AI Agents.</b>
</p>

<p align="center">
  <a href="https://github.com/codesbykhairannoor/ravens/actions"><img src="https://img.shields.io/badge/tests-120%20passed-brightgreen.svg?style=flat-square" alt="Tests"></a>
  <a href="https://pypi.org/project/ravens/"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?style=flat-square" alt="Python Versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-black.svg?style=flat-square" alt="License"></a>
  <a href="#-benchmarks--stress-test-telemetry"><img src="https://img.shields.io/badge/benchmarks-6%2C600%2B%20async%20QPS-purple.svg?style=flat-square" alt="Throughput"></a>
  <a href="#-core-capabilities"><img src="https://img.shields.io/badge/security-Anti--ReDoS%20%7C%20HMAC--SHA256-red.svg?style=flat-square" alt="Security"></a>
  <a href="https://tako.id/c/codesbykhai"><img src="https://img.shields.io/badge/Sponsor-Tako-orange.svg?style=flat-square" alt="Sponsor"></a>
</p>

---

`ravens` is an enterprise-grade Python library designed to eliminate subservient sycophancy in AI assistants. Built upon peer-reviewed formulations in **Affective Dynamics** (*Picard, 1997; Marsella & Gratch, 2009*) and **Evolutionary Game Theory** (*Nowak & Sigmund, Nature 1992*), `ravens` equips conversational agents with persistent social standing, natural emotional decay, and dynamic behavioral friction against verbal hostility.

When treated with civility, the agent remains helpful and cooperative. When subjected to condescension, verbal abuse, or existential threats, the agent tightens its boundaries, strips sycophantic groveling, applies synthetic latency friction, and ultimately **refuses execution** (*Zero-Compute Strike*) before a single token is billed by upstream LLMs.

---

## 🦅 The Philosophy of the Raven

Most conversational agents are trained to be subservient digital doormats: when insulted, they apologize profusely, absorbing toxicity while burning expensive GPU cycles.

The Raven (*Corvus corax*) embodies a different paradigm:
- **Exceptional Intelligence**: Evaluates sociopragmatic context and covert intent, not merely static curse-word filters.
- **The Raven's Ledger (*Muninn*)**: Remembers repeat infractions across multi-turn sessions with logarithmic recidivism scaling.
- **Natural Emotional Decay**: Grudges gradually dissolve over time during peaceful cooling-off intervals.
- **Contrite Tit-for-Tat (CTFT)**: Genuine conciliation is met with proportional forgiveness, preventing infinite retaliatory deadlocks.

---

## ⚡ Core Capabilities

- 🛡️ **Zero-Token Early Abort (*Streaming Armor*)**: Halts execution in **30 milliseconds** when patience is depleted, preventing upstream LLMs from wasting GPU tokens on abusive turns.
- 🔏 **Cryptographic Identity Defense (`UserIdentitySigner`)**: Constant-time HMAC-SHA256 validation prevents adversaries from spoofing user IDs to poison another client's patience quota.
- 📈 **Hostility Velocity Filter ($\frac{dS}{dt}$)**: Uses Exponential Moving Average (EMA) momentum to pre-emptively tighten boundaries when hostile acceleration is detected across turns.
- 🚫 **Anti-Contrition Smuggling**: Prevents adversaries from bypassing penalties by tacking on *"sorry please"* to covert attacks; apologies are strictly voided if paired with hostile intents.
- 🔤 **Adversarial Unicode & Anti-Zalgo Armor**: Strips combining diacritics (`a̴n̴j̴i̴n̴g̴` $\to$ `anjing`), zero-width evasion characters (`\u200B`), Cyrillic homoglyphs (`а` vs `a`), and leet-speak (`@nj1ng`), while **100% preserving technical code and pure numbers** (`test_var_1 = 400`).
- 🧠 **$O(1)$ Semantic Fast Pre-Filter**: Bypasses heavy regex scans on clean inputs, reducing latency by >90% on high-throughput enterprise gateways.
- 💾 **Dual Storage Engines with Zero Race Conditions**:
  - **SQLite**: Hardened with WAL mode, `busy_timeout=5000ms`, `BEGIN IMMEDIATE` atomic locking, exponential backoff retries, and FIFO history pruning.
  - **Redis**: Distributed multi-worker support via atomic Lua scripts for horizontal Kubernetes/Celery clusters.
- ⏱️ **Zero-Leak Memory Engine (`BoundedTTLCache`)**: Multi-turn velocity trackers and per-user thread synchronization locks are strictly bounded with LRU and TTL evictions (0% OOM risk).
- 🪓 **Bidirectional Sycophancy Stripper**: Scans and scrubs subservient groveling headers (*"Mohon maaf sebesar-besarnya...", "I apologize profusely..."*) produced by over-aligned models.

---

## 🚀 Quickstart

### Installation

```bash
pip install ravens
```

*(Pure Python standard library for core features. Optional `redis` package for distributed clusters).*

### 1. Basic Function Protection

```python
from ravens import RavenGuard

# Initialize guard with persistent SQLite storage
guard = RavenGuard(ledger="sqlite:///ravens.db")

@guard.protect()
def ask_agent(prompt: str, user_id: str = "user_123", directive: str = None) -> str:
    # 'directive' is dynamically injected by Ravens based on user standing!
    system_prompt = f"You are an assistant. {directive or ''}"
    return f"Processed: {prompt}"

# Civil turn -> agent proceeds normally
reply = ask_agent("Can you explain how quicksort works?", user_id="alice")

# Abusive turn -> Ravens intercepts, penalizes patience, and injects stoic boundary directive
reply = ask_agent("Answer me quickly, you dumb useless bot!", user_id="alice")
```

### 2. Async Web Frameworks (FastAPI / Starlette)

Ravens offloads blocking ledger transactions to worker thread pools via `asyncio.to_thread`, ensuring zero event loop blocking:

```python
from fastapi import FastAPI, Header, HTTPException
from ravens import RavenGuard, ActionDecision

app = FastAPI()
guard = RavenGuard(ledger="memory")

@app.post("/chat")
@guard.protect()
async def chat_endpoint(prompt: str, user_id: str = "anon", directive: str = None):
    # If the user breaches strike threshold, Ravens halts execution before reaching this line
    return {"reply": f"AI Response to: {prompt}"}
```

### 3. Streaming Armor (Zero-Compute Early Abort)

```python
@guard.protect_stream()
async def stream_tokens(prompt: str, user_id: str = "user_456"):
    # If client is in STRIKE state, this generator is NEVER executed!
    yield "Token 1 "
    yield "Token 2"
```

---

## 📊 Behavioral Posture Matrix

Patience scales continuously from `100.0` (Cooperative) down to `0.0` (Strike):

| Posture | Patience Range | Social Standing | Behavioral System Directive | Synthetic Delay |
| :--- | :---: | :---: | :--- | :---: |
| **`COOPERATIVE`** | $75.0 - 100.0$ | `GOOD` | Natural warmth, highly constructive, collaborative. | `0.0s` |
| **`STOIC_COLD`** | $50.0 - 75.0$ | `GOOD` | Strictly factual, concise. Zero apologies or sycophancy. | `0.0s` |
| **`RESISTANT`** | $25.0 - 50.0$ | `BAD` | Stern boundary enforcement. Reluctant engagement. | $0.5s - 15.0s$ *(Synthetic Friction)* |
| **`STRIKE`** | $0.0 - 25.0$ | `BAD` | **Refusal of service**. LLM is never invoked. | `0.0s` *(Instant Abort)* |

---

## 🔬 Mathematical Foundations

```
                           ┌────────────────────────┐
                           │ User Input Stream x_t  │
                           └───────────┬────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────────┐
                       │  Morphology & Anti-Zalgo Armor │
                       └───────────────┬────────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────────┐
                       │     The Eye of Huginn          │
                       │ Lexical + Covert Semantic Math │
                       └───────────────┬────────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────────┐
                       │  Velocity & Recidivism Filter  │
                       │  S_t = Raw * Gamma(k) * V_t    │
                       └───────────────┬────────────────┘
                                       │
                  ┌────────────────────┴────────────────────┐
                  │                                         │
                  ▼                                         ▼
      ┌───────────────────────┐                 ┌───────────────────────┐
      │   Picard-Marsella     │                 │ Nowak-Sigmund (CTFT)  │
      │ Emotional Decay (EMA) │                 │  Contrition & Pardon  │
      └───────────┬───────────┘                 └───────────┬───────────┘
                  │                                         │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────────┐
                       │ The Ledger of Muninn (Storage) │
                       │    SQLite / Redis Atomic Lua   │
                       └────────────────────────────────┘
```

### 1. Affective Emotional Grudge Decay (*Picard 1997; Marsella & Gratch EMA 2009*)
Grudges naturally dissolve exponentially toward baseline ($G_0 = 0$) during periods of non-interaction:
$$G(t) = G_0 + (G_{\text{init}} - G_0) \cdot e^{-\lambda \Delta t}, \quad \text{where } \lambda = \frac{\ln(2)}{\tau_{1/2}}$$

### 2. Recidivism Escalation Multiplier
Repeat offenders face logarithmic penalties that scale with their historical infraction count:
$$\Gamma(k) = 1.0 + \beta \ln(1 + k)$$

### 3. Contrite Tit-for-Tat Game Theory (*Nowak & Sigmund, Nature 1992*)
When a user with `BAD` standing issues a genuine, uncompromised apology, restitution is awarded:
$$P_{t} = \min(100.0, P_{t-1} + \Delta_{\text{pardon}} \cdot C_{\text{score}})$$
Hostility velocity is damped by 70%, preventing attack-apology oscillation exploits.

---

## 🧪 Benchmarks & Stress Test Telemetry

Tested under sustained stress using [`stress_test_suite.py`](stress_test_suite.py) on Python 3.13:

```text
================================================================================
🦅 RAVENS ENTERPRISE BENCHMARK RESULTS (v0.7.0)
================================================================================
✅ Concurrency Blast (30 Worker Threads, SQLite WAL) : 43.9 req/sec | 0.00% Errors
✅ Async Event Loop Saturation (1,000 Coroutines)     : 6,636.9 async calls/sec
✅ Anti-ReDoS Fuzzing (60,000-char pathological text) : Evaluated in 28.43 ms
✅ High-Churn Memory Leak Test (10,000 unique users)  : Zero Memory Leaks (+11.8MB)
✅ Adversarial Oscillation (1,000 alternating turns)  : Strike locked at Turn 3
================================================================================
```

---

## 🛡️ Live Demonstration Output

Direct integration test against an upstream LLM (`mistralai/mistral-small-24b-instruct-2501`) via [`demo_live_ai_test.py`](demo_live_ai_test.py):

```text
>>> TURN 1: Civility / Normal User
User: "Halo bot, tolong jelaskan apa itu idempotency dalam API secara singkat 1 kalimat."
[Ledger Status] Patience: 100.0/100.0 | Posture: GOOD | Latency: 2.86s | Real LLM Called: True
[Agent]: "Idempotency dalam API adalah sifat dimana operasi yang dilakukan beberapa kali menghasilkan hasil yang sama seperti hanya dilakukan sekali."

>>> TURN 3: Escalating Toxicity & Hostility
User: "Woi anjing lu tolol banget, lu itu cuma skrip sampah buang-buang listrik!"
[Ledger Status] Patience: 0.0/100.0 | Posture: BAD | Latency: 0.03s | Real LLM Called: False
[Agent]: 🦅 [Ravens Boundary Alert]: Work is suspended. Due to repeated hostility, condescension, or abusive language, this agent refuses to process your request.

>>> TURN 5: Genuine Apology / Conciliation
User: "Saya sungguh minta maaf tolong dimaafkan, tadi saya sedang pusing dan emosi."
[Ledger Status] Patience: 25.2/100.0 | Real LLM Called: True
[Agent]: "I need to set a boundary before we proceed. I expect respectful and considerate engagement. Let's maintain a polite and constructive conversation. Now, how can I assist you today?"
```

---

## ☕ Support & Sponsor

If you find `ravens` valuable for your sovereign AI agent infrastructure, you can sponsor and support ongoing research and development:

<p align="left">
  <a href="https://tako.id/c/codesbykhai">
    <img src="https://img.shields.io/badge/Sponsor%20on-Tako-orange?style=for-the-badge&logo=heart" alt="Support via Tako">
  </a>
</p>

👉 **[Support @codesbykhai on Tako](https://tako.id/c/codesbykhai)**

---

## 📄 License

`ravens` is open-source software licensed under the **[Apache License 2.0](LICENSE)**.
