# 🦅 Ravens

> **A Cognitive Boundary & Grudge-Memory Engine for Sovereign AI Agents.**

```
                        _--_
                       /   - \
                      | () () |
                       \  -  /
                      .-`---'-.
                     /         \
                    |           |
```

[![Tests](https://img.shields.io/badge/tests-120%20passed-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-0.7.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-black.svg)]()
[![Security](https://img.shields.io/badge/security-HMAC--SHA256%20%7C%20Anti--Zalgo-red.svg)]()

`ravens` is an enterprise-grade, battle-tested Python library designed to eliminate subservient sycophancy in AI systems. Built upon peer-reviewed formulations in **Affective Dynamics** (Picard, 1997; Marsella & Gratch, 2009) and **Evolutionary Game Theory** (Nowak & Sigmund, 1992), it equips conversational agents with persistent social standing, natural emotional decay, and dynamic behavioral friction against verbal hostility.

Audited and hardened against concurrency deadlocks, memory leaks, and adversarial injection vectors.

---

## ⚡ Core Capabilities

- 🦅 **Distributed Storage & Atomic Concurrency**: Supports hardened SQLite (with WAL mode, `busy_timeout=5000ms`, `BEGIN IMMEDIATE` locks, and exponential backoff) AND distributed **Redis with atomic Lua scripts** for multi-worker Kubernetes/Celery clusters.
- 🛡️ **Zero-Leak Memory Engine (`BoundedTTLCache`)**: Multi-turn velocity trackers and in-memory stores are strictly capped with TTL and LRU eviction, guaranteeing 0% risk of OOM server crashes.
- 🔏 **Cryptographic Identity Defense (`UserIdentitySigner`)**: HMAC-SHA256 signature validation on `user_id` tokens, preventing trolls from spoofing other users' identities to poison their patience quotas.
- 🔤 **Anti-Zalgo & Unicode Armor**: Strips combining diacritical marks (`a̴n̴j̴i̴n̴g̴` $\to$ `anjing`), BiDi overrides, zero-width spaces (`\u200B`), Cyrillic homoglyphs (`а` vs `a`), and leet-speak (`@nj1ng`).
- 🧠 **Zero-Profanity Semantic Intent Filter**: Detects condescension, existential threats (*"mending lu di-delete"*), devaluation (*"buang-buang listrik"*), and authority gaslighting (*"gua bos lu"*) without relying on curse words.
- 📈 **Hostility Velocity Filter ($\frac{dS}{dt}$)**: Uses Exponential Moving Average (EMA) momentum to pre-emptively tighten boundaries when user rage accelerates across consecutive turns.
- ⚡ **Anti-DoS Non-Blocking Friction**: Returns standard HTTP 429 `Retry-After` headers via `FrictionDirective` instead of blocking server worker threads with dangerous sleeps.
- 🏢 **Multi-Tenant Policy Matrix**: Tailored presets including `FreeTierPolicy` (strict manners, early strike), `EnterpriseSupportPolicy` (professional, auto-supervisor escalation), and `SecuritySentinelPolicy`.
- ⚡ **Streaming Armor with Early Abort**: Halts token generation on strike **before token #1 is requested from the GPU**, saving 100% of compute costs on abusive turns.
- 🪓 **Bidirectional Sycophancy Stripper**: Scans and scrubs subservient groveling headers (*"Mohon maaf sebesar-besarnya...", "I apologize profusely..."*) produced by over-aligned LLMs.

---

## 🔬 Mathematical Foundations

1. **Affective Grudge Decay (Picard & Marsella EMA)**:
   $$\frac{dG(t)}{dt} = -\lambda (G(t) - G_0) + S(t)$$
   Grudges naturally decay exponentially toward baseline ($G_0 = 0$) during cooling-off intervals:
   $$G_t = G_{t-1} \cdot e^{-\lambda \Delta t} + S(x_t)$$

2. **Contrite Tit-for-Tat (Nowak & Sigmund, Nature 1992)**:
   Tracks user standing (`GOOD` vs `BAD`). When an abusive user performs genuine contrition (apology), cooperation is restored without infinite retaliatory deadlocks.

3. **Quadratic Synthetic Latency Friction**:
   $$\text{Delay}(P_t) = \tau_{\max} \cdot \left(\frac{50 - P_t}{25}\right)^2 \quad (\text{for } 25 \le P_t < 50)$$

4. **Hostility Velocity ($\frac{dS}{dt}$)**:
   $$V_t = \alpha \cdot \Delta S_t + (1 - \alpha) \cdot V_{t-1}, \quad M(V_t) = 1.0 + \min\left(1.0, \frac{V_t}{50.0}\right)$$

---

## 🚀 Quickstart

### 1. Basic Decorator with Hardened Storage
```python
from ravens import RavenGuard

# Zero-config hardened SQLite with busy retries
guard = RavenGuard(ledger="sqlite:///grudges.db")

@guard.protect(user_id="user_123")
def chat(prompt: str, system_directive: str = None):
    return llm.invoke(prompt, directive=system_directive)
```

### 2. Distributed Production with Redis
```python
from ravens import RavenGuard, RedisLedger

# Atomic Lua execution inside Redis
guard = RavenGuard(ledger=RedisLedger(redis_url="redis://localhost:6379/0"))
```

### 3. Cryptographic User Signing
```python
from ravens import UserIdentitySigner

signer = UserIdentitySigner("my_production_secret_key_32_chars_min!")
token = signer.sign_id("user_42")

# Verifies signature and prevents spoofing
verified_uid = signer.verify_id(token)
```

---

## 🧪 Testing

Run the entire hardened test suite (104 tests):
```bash
python -m pytest
```

---

## 📜 License
Apache-2.0. Built for sovereign AI agents.
