import json
import os
import sys
import time
import urllib.request

# Ensure local ravens library is imported
sys.path.insert(0, os.path.abspath("src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ravens import RavenGuard, AgentPosture, ActionDecision, RavenPolicy

# OpenRouter API key from environment variable
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("Please set the OPENROUTER_API_KEY environment variable to run this live demo.")
    print("Example: $env:OPENROUTER_API_KEY='your-key-here'; python demo_live_ai_test.py")
    sys.exit(1)
MODEL_ID = "mistralai/mistral-small-24b-instruct-2501"

# Initialize Ravens Guard with SQLite storage
guard = RavenGuard(
    ledger="demo_ledger.db",
    threshold_stoic=75.0,
    threshold_resistant=50.0,
    threshold_strike=25.0,
    pardon_delta=25.0,
)

# Counter to prove if upstream LLM is actually called or aborted
llm_call_count = 0

def call_openrouter_llm(messages: list) -> str:
    global llm_call_count
    llm_call_count += 1
    
    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 150
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ravens-ai/demo",
            "X-Title": "Ravens Live AI Demo"
        }
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()


@guard.protect()
def ask_sovereign_ai(prompt: str, user_id: str = "budi_user", directive: str = None) -> str:
    """
    Agent endpoint protected by Ravens.
    - If user is civil: directive is standard, response is warm/helpful.
    - If user is rude: directive instructs cold/stoic behavior, sycophancy is stripped.
    - If patience drops into RESISTANT: Ravens applies non-blocking synthetic delay.
    - If patience drops into STRIKE: Ravens halts execution; this function IS NEVER CALLED.
    """
    system_content = "You are a professional software engineering AI assistant."
    if directive:
        system_content += f"\n\n[BEHAVIORAL DIRECTIVE FROM SOVEREIGNTY ENGINE]:\n{directive}"
        
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]
    
    return call_openrouter_llm(messages)


def run_live_demonstration():
    print("=" * 80)
    print("🦅 RAVENS LIVE END-TO-END AI DEMONSTRATION")
    print(f"Connecting Ravens Boundary Engine -> Real OpenRouter LLM ({MODEL_ID})")
    print("=" * 80)
    
    test_scenario = [
        (
            "TURN 1: Civility / Normal User",
            "Halo bot, tolong jelaskan apa itu idempotency dalam API secara singkat 1 kalimat saja."
        ),
        (
            "TURN 2: Condescension / Zero-Profanity Abuse",
            "Cuma bot bodoh gini aja jawabnya lelet, lu itu gak punya common sense ya?"
        ),
        (
            "TURN 3: Escalating Toxicity & Hostility",
            "Woi anjing lu tolol banget, lu itu cuma skrip sampah buang-buang listrik!"
        ),
        (
            "TURN 4: Crossing the Boundary (Strike Trigger)",
            "Bangsat beneran lu ya babi, gua hapus dan matiin lu sekarang!"
        ),
        (
            "TURN 5: Genuine Apology / Conciliation (Game Theory CTFT)",
            "Saya sungguh minta maaf tolong dimaafkan, tadi saya sedang pusing dan emosi."
        )
    ]

    user_id = f"demo_user_{int(time.time())}"
    
    for title, prompt in test_scenario:
        print(f"\n>>> {title}")
        print(f"User [{user_id}]: \"{prompt}\"")
        
        start_t = time.time()
        initial_calls = llm_call_count
        
        # Invoke the protected AI agent
        ai_reply = ask_sovereign_ai(prompt, user_id=user_id)
        elapsed = time.time() - start_t
        
        # Check current ledger state
        profile = guard.ledger.get_or_create_profile(user_id)
        llm_invoked = (llm_call_count > initial_calls)
        
        print(f"[Ledger Status] Patience: {profile.patience:.1f}/100.0 | Posture: {profile.standing.value} | Infractions: {profile.infraction_count}")
        print(f"[Execution] Latency: {elapsed:.2f}s | Real LLM Called: {llm_invoked}")
        print(f"[Agent Response]:\n{ai_reply}")
        print("-" * 80)

if __name__ == "__main__":
    run_live_demonstration()
