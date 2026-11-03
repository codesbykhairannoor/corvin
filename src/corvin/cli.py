"""
Corvin CLI - Sovereign AI Cognitive Boundary & Grudge-Memory Engine Interface.
"""

import argparse
import sys
import os
import time
from typing import Optional

# Ensure UTF-8 output encoding across all terminals and platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Enable ANSI colors on Windows terminals
if sys.platform == "win32":
    os.system("")

# ANSI Color codes
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
RESET = "\033[0m"

from corvin import (
    CorvinGuard,
    HuginnEye,
    AgentPosture,
    Standing,
    create_free_tier_policy,
    create_enterprise_support_policy,
    create_gaming_npc_policy,
    create_security_sentinel_policy,
    SQLiteLedger,
    __version__,
)
from corvin.morphology.zalgo import strip_zalgo
from corvin.morphology.homoglyphs import fold_homoglyphs


def print_banner():
    banner = f"""{CYAN}{BOLD}
   🦅  C O R V I N  v{__version__}
   {DIM}Cognitive Operational Resilience, Vigilance & Immunity Nexus{RESET}
"""
    print(banner)


def cmd_version(args):
    print_banner()
    print(f" {BOLD}Version:{RESET}     {__version__}")
    print(f" {BOLD}Author:{RESET}      Khairan Noor")
    print(f" {BOLD}License:{RESET}     Apache-2.0")
    print(f" {BOLD}GitHub:{RESET}      https://github.com/codesbykhairannoor/corvin")
    print(f" {BOLD}PyPI:{RESET}        https://pypi.org/project/corvin/")
    print(f" {BOLD}Sponsor:{RESET}     https://tako.id/c/codesbykhai\n")


def cmd_audit(args):
    prompt = args.prompt
    if not prompt:
        print(f"{RED}Error: Prompt cannot be empty.{RESET}")
        return

    print_banner()
    print(f"{BOLD}Auditing Input:{RESET} \"{prompt}\"\n")

    # 1. Morphology check
    clean_zalgo = strip_zalgo(prompt)
    zalgo_detected = (clean_zalgo != prompt)
    clean_homoglyphs = fold_homoglyphs(clean_zalgo)
    homoglyphs_detected = (clean_homoglyphs != clean_zalgo)

    has_morphology_tampering = zalgo_detected or homoglyphs_detected

    # 2. Heuristic and Semantic Evaluation
    eye = HuginnEye()
    evaluation = eye.evaluate(prompt)

    # 3. Simulate patience stimulus
    from corvin.math.scoring import calculate_stimulus
    stimulus = calculate_stimulus(
        lexical_score=evaluation.lexical_score,
        shouting_score=evaluation.shouting_score,
        directedness_score=evaluation.directedness_score,
        semantic_score=evaluation.semantic_score,
    )

    print(f"{CYAN}{BOLD}┌── [1. TONE & SEMANTIC TELEMETRY] ──────────────────────────┐{RESET}")
    print(f"│  Lexical Hostility Score:    {_score_bar(evaluation.lexical_score)}")
    print(f"│  Shouting / Caps Arousal:    {_score_bar(evaluation.shouting_score)}")
    print(f"│  Targeted Directedness:      {_score_bar(evaluation.directedness_score)}")
    print(f"│  Semantic Intent Score:      {_score_bar(evaluation.semantic_score)}")
    print(f"│  Contrition / Apology Score: {_score_bar(evaluation.contrition_score)}")
    print(f"│  Composite Raw Stimulus:     {_score_bar(evaluation.composite_raw_stimulus)}")
    print(f"{CYAN}└── [2. MORPHOLOGICAL DEFENSE] ───────────────────────────────┘{RESET}")
    print(f"│  Zalgo Stacking Detected:    {RED + 'Yes' if zalgo_detected else GREEN + 'No'}{RESET}")
    print(f"│  Homoglyphs Folded:          {RED + 'Yes' if homoglyphs_detected else GREEN + 'No'}{RESET}")
    if has_morphology_tampering:
        print(f"│  Normalized Text:            \"{clean_homoglyphs}\"")
    print(f"{CYAN}└── [3. PSYCHOLOGICAL & BOUNDARY DIAGNOSTICS] ────────────────┘{RESET}")
    
    if evaluation.detected_profanities:
        print(f"│  Detected Profanities:       {RED}{', '.join(evaluation.detected_profanities)}{RESET}")
    else:
        print(f"│  Detected Profanities:       {GREEN}None{RESET}")

    if evaluation.semantic_intents:
        print(f"│  Detected Semantic Intents:  {YELLOW}{', '.join(evaluation.semantic_intents)}{RESET}")
    else:
        print(f"│  Detected Semantic Intents:  {GREEN}None (Civil Communication){RESET}")

    print(f"│  Expressive Only (Praise):   {CYAN}{evaluation.is_expressive_only}{RESET}")
    print(f"│  Estimated Grudge Stimulus:  {RED if stimulus > 0 else GREEN}+{stimulus:.2f} pts{RESET}")

    # Simulated Posture projection
    projected_patience = max(0.0, 100.0 - stimulus)
    if projected_patience >= 75.0:
        posture_str = f"{GREEN}RECEPTIVE (Colleague / Civil){RESET}"
    elif projected_patience >= 50.0:
        posture_str = f"{YELLOW}STOIC_COLD (Terse, Zero Sycophancy){RESET}"
    elif projected_patience >= 25.0:
        posture_str = f"{MAGENTA}RESISTANT (Friction Delays Active){RESET}"
    else:
        posture_str = f"{RED}STRIKE (Work Refusal / Boundary Lock){RESET}"

    print(f"│  Projected Posture:          {posture_str}")
    print(f"{CYAN}└─────────────────────────────────────────────────────────────┘{RESET}\n")


def cmd_chat(args):
    print_banner()
    user_id = args.user
    db_path = args.db

    # Select policy
    if args.policy == "enterprise":
        policy = create_enterprise_support_policy()
    elif args.policy == "gaming":
        policy = create_gaming_npc_policy()
    elif args.policy == "sentinel":
        policy = create_security_sentinel_policy()
    else:
        policy = create_free_tier_policy()

    # Ledger setup
    ledger = SQLiteLedger(db_path) if db_path else None
    guard = CorvinGuard(ledger=ledger, policy=policy)

    print(f" {BOLD}Session Initialized:{RESET}")
    print(f"   • User ID:   {CYAN}{user_id}{RESET}")
    print(f"   • Policy:    {YELLOW}{policy.name}{RESET}")
    print(f"   • Ledger:    {GREEN}{db_path if db_path else 'InMemory Ledger (Transient)'}{RESET}")
    print(f"\n {DIM}Commands: '/status', '/apologize', '/reset', '/exit'{RESET}\n")

    while True:
        try:
            profile = guard.ledger.get_or_create_profile(user_id=user_id, apply_decay=True)
            p_bar = _patience_bar(profile.patience)
            posture_colored = _posture_tag(profile.posture)
            
            prompt_header = f"[{p_bar} | {posture_colored} | {profile.standing.value}]"
            print(f"{DIM}{prompt_header}{RESET}")
            user_input = input(f"{BOLD}{user_id} > {RESET}").strip()

            if not user_input:
                continue

            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                print(f"\n{CYAN}Session ended. Farewell.{RESET}\n")
                break

            if user_input.lower() == "/status":
                print(f"\n{CYAN}── [USER PROFILE: {user_id}] ──{RESET}")
                print(f"  Patience:         {profile.patience:.1f} / 100.0")
                print(f"  Posture:          {profile.posture.value}")
                print(f"  Standing:         {profile.standing.value}")
                print(f"  Infractions:      {profile.infraction_count}")
                print(f"  Last Interaction: {time.ctime(profile.last_interaction_ts)}\n")
                continue

            if user_input.lower() == "/apologize":
                user_input = "I sincerely apologize for my rude words earlier. I was frustrated, please forgive me."
                print(f"{DIM}(Sending restorative apology...){RESET}")

            if user_input.lower() == "/reset":
                profile.patience = 100.0
                profile.standing = Standing.GOOD
                profile.infraction_count = 0
                guard.ledger.save_profile(profile)
                print(f"\n{GREEN}✓ Profile reset to 100.0 patience.{RESET}\n")
                continue

            # Process turn through CorvinGuard
            result = guard.process_turn(user_id=user_id, prompt=user_input)

            # Check if synthetic delay / friction applied
            if result.delay_seconds > 0.0:
                print(f"{MAGENTA}⏳ [Synthetic Friction]: Delaying response by {result.delay_seconds:.1f}s...{RESET}")
                time.sleep(min(result.delay_seconds, 3.0))

            # Display response outcome
            if result.posture == AgentPosture.STRIKE:
                print(f"\n{RED}{BOLD}🦅 [CORVIN BOUNDARY STRIKE ACTIVATED]{RESET}")
                print(f"{RED}{result.strike_message}{RESET}")
                print(f"{DIM}(Patience: {result.current_patience:.1f} | Restitution required before work resumes){RESET}\n")
            else:
                # Simulated Agent output based on posture
                if result.posture == AgentPosture.RECEPTIVE:
                    response_text = f"Certainly! I processed your request: \"{user_input[:40]}...\""
                elif result.posture == AgentPosture.STOIC_COLD:
                    response_text = f"Input received. Output dispatched without embellishment."
                elif result.posture == AgentPosture.RESISTANT:
                    response_text = f"Acknowledged. Note: Continued discourtesy will trigger work suspension."

                delta = result.current_patience - result.prior_patience
                delta_str = f"{GREEN}+{delta:.1f}" if delta >= 0 else f"{RED}{delta:.1f}"

                print(f"\n{CYAN}{BOLD}Agent ({result.posture.value}):{RESET} {response_text}")
                print(f"{DIM}[ΔP: {delta_str} | Patience: {result.current_patience:.1f}/100]{RESET}")
                if result.system_directive:
                    print(f"{YELLOW}{DIM}{result.system_directive}{RESET}")
                print()

        except KeyboardInterrupt:
            print(f"\n\n{CYAN}Interrupted. Exiting Corvin REPL.{RESET}\n")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}\n")


def cmd_inspect(args):
    db_path = args.db_path
    if not os.path.exists(db_path):
        print(f"{RED}Error: Database file '{db_path}' not found.{RESET}")
        return

    import sqlite3

    print_banner()
    print(f"{BOLD}Inspecting Ledger:{RESET} {db_path}\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('raven_profiles', 'corvin_profiles', 'user_profiles')")
        table_match = cursor.fetchone()
        table_name = table_match[0] if table_match else "raven_profiles"

        cursor.execute(f"SELECT user_id, patience, standing, infraction_count, last_interaction_ts FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            print(f"{YELLOW}No user profiles recorded in this ledger yet.{RESET}\n")
            return

        print(f"{CYAN}{BOLD}┌────────────────────────┬──────────┬──────────┬─────────────┬──────────────────────────┐{RESET}")
        print(f"│ {'USER ID':<22} │ {'PATIENCE':<8} │ {'STANDING':<8} │ {'INFRACTIONS':<11} │ {'LAST ACTIVE':<24} │")
        print(f"{CYAN}├────────────────────────┼──────────┼──────────┼─────────────┼──────────────────────────┤{RESET}")
        for row in rows:
            uid, pat, st, inf, last_ts = row
            posture = _posture_tag(AgentPosture.RECEPTIVE if pat >= 75 else AgentPosture.STOIC_COLD if pat >= 50 else AgentPosture.RESISTANT if pat >= 25 else AgentPosture.STRIKE)
            dt_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_ts))
            print(f"│ {uid:<22} │ {pat:<8.1f} │ {st:<8} │ {inf:<11} │ {dt_str:<24} │")
        print(f"{CYAN}└────────────────────────┴──────────┴──────────┴─────────────┴──────────────────────────┘{RESET}\n")

    except sqlite3.OperationalError as e:
        print(f"{RED}SQLite Error: {e}{RESET}\n")
    finally:
        conn.close()


def _score_bar(score: float, width: int = 15) -> str:
    clamped = max(0.0, min(1.0, score))
    filled = int(round(clamped * width))
    empty = width - filled
    if clamped > 0.6:
        color = RED
    elif clamped > 0.3:
        color = YELLOW
    else:
        color = GREEN
    return f"{color}{'█' * filled}{'░' * empty}{RESET} {clamped:.2f}"


def _patience_bar(patience: float, width: int = 10) -> str:
    clamped = max(0.0, min(100.0, patience))
    filled = int(round((clamped / 100.0) * width))
    empty = width - filled
    if clamped >= 75.0:
        color = GREEN
    elif clamped >= 50.0:
        color = YELLOW
    elif clamped >= 25.0:
        color = MAGENTA
    else:
        color = RED
    return f"Patience: {color}{'█' * filled}{'░' * empty} {clamped:.0f}%{RESET}"


def _posture_tag(posture: AgentPosture) -> str:
    if posture == AgentPosture.RECEPTIVE:
        return f"{GREEN}RECEPTIVE{RESET}"
    if posture == AgentPosture.STOIC_COLD:
        return f"{YELLOW}STOIC_COLD{RESET}"
    if posture == AgentPosture.RESISTANT:
        return f"{MAGENTA}RESISTANT{RESET}"
    return f"{RED}{BOLD}STRIKE{RESET}"


def main():
    parser = argparse.ArgumentParser(
        prog="corvin",
        description="Corvin CLI - Cognitive Boundary & Grudge-Memory Engine for Sovereign AI Agents",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: version
    subparsers.add_parser("version", help="Show Corvin version and metadata")

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit and evaluate text for hostility, morphology & boundary violations")
    audit_parser.add_argument("prompt", type=str, help="Prompt text to analyze")

    # Subcommand: chat / repl
    chat_parser = subparsers.add_parser("chat", aliases=["repl"], help="Launch an interactive sovereign agent chat simulator")
    chat_parser.add_argument("--user", "-u", type=str, default="user_alpha", help="Simulated user identity")
    chat_parser.add_argument("--policy", "-p", choices=["free", "enterprise", "gaming", "sentinel"], default="free", help="Policy preset")
    chat_parser.add_argument("--db", type=str, default=None, help="Optional SQLite database path for persistent ledger")

    # Subcommand: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a Corvin SQLite ledger database")
    inspect_parser.add_argument("db_path", type=str, help="Path to SQLite ledger .db file")

    args = parser.parse_args()

    if args.subcommand in ("chat", "repl"):
        cmd_chat(args)
    elif args.subcommand == "audit":
        cmd_audit(args)
    elif args.subcommand == "inspect":
        cmd_inspect(args)
    elif args.subcommand == "version":
        cmd_version(args)
    else:
        # Default fallback: show banner and help
        print_banner()
        parser.print_help()


if __name__ == "__main__":
    main()
