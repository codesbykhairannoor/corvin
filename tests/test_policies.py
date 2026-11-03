import pytest

from ravens.policies import (
    RavenPolicy,
    create_free_tier_policy,
    create_enterprise_support_policy,
    create_gaming_npc_policy,
    create_security_sentinel_policy,
    InMemoryEventNotifier,
)
from ravens.guard.core import RavenGuard
from ravens.storage.memory import InMemoryLedger
from ravens.core.state import AgentPosture
from ravens.core.exceptions import RavenStrikeException


class TestPolicyPresets:
    def test_free_tier_policy_strikes_early(self):
        policy = create_free_tier_policy()
        assert policy.threshold_strike == 40.0
        assert "Free-Tier Guard" in policy.strike_message
        assert policy.max_delay_seconds == 25.0

    def test_enterprise_policy_high_tolerance(self):
        policy = create_enterprise_support_policy()
        assert policy.threshold_strike == 15.0
        assert "Enterprise Support Notice" in policy.strike_message
        assert policy.custom_metadata["escalate_to_human"] is True

    def test_gaming_npc_policy_metadata(self):
        policy = create_gaming_npc_policy(npc_name="Geralt")
        assert policy.custom_metadata["npc_name"] == "Geralt"
        assert policy.custom_metadata["shop_price_multiplier"] == 2.0
        assert "Geralt" in policy.strike_message

    def test_security_sentinel_policy_raises(self):
        policy = create_security_sentinel_policy()
        assert policy.raise_on_strike is True
        assert policy.threshold_strike == 60.0


class TestPolicyEventDispatching:
    def test_strike_and_breach_callbacks(self):
        notifier = InMemoryEventNotifier()
        policy = create_enterprise_support_policy(
            on_boundary_breach=notifier.on_boundary_breach,
            on_strike=notifier.on_strike,
        )
        guard = RavenGuard(ledger=InMemoryLedger(), policy=policy)

        # 1. Mild attack triggers boundary breach callback
        guard.process_turn("corp_user_1", "Lu bego banget deh")
        assert len(notifier.events) >= 1
        assert notifier.events[0].event_type == "BOUNDARY_BREACH"
        assert notifier.events[0].user_id == "corp_user_1"

        # 2. Repeated hostile attack triggers strike callback
        guard.process_turn("corp_user_1", "Bangsat anjing lu gak guna!")
        guard.process_turn("corp_user_1", "Lu tolol babi!")

        strike_events = [e for e in notifier.events if e.event_type == "STRIKE"]
        assert len(strike_events) >= 1
        assert strike_events[0].user_id == "corp_user_1"


class TestMultiTenantPolicyRouting:
    def test_same_guard_different_tenant_policies(self):
        guard = RavenGuard(ledger=InMemoryLedger())

        free_policy = create_free_tier_policy()
        enterprise_policy = create_enterprise_support_policy()

        attack_prompt = "Lu tolol banget sih!"

        # Free tier user: with threshold_strike=40, this hostile attack drops them straight to STRIKE or RESISTANT
        res_free = guard.process_turn("free_user_1", attack_prompt, policy=free_policy)
        assert res_free.posture == AgentPosture.RESISTANT or res_free.posture == AgentPosture.STRIKE

        # Enterprise user: with higher tolerance (threshold_strike=15, threshold_resistant=40),
        # they stay in STOIC_COLD on the first attack
        res_enterprise = guard.process_turn("enterprise_user_1", attack_prompt, policy=enterprise_policy)
        assert res_enterprise.posture == AgentPosture.STOIC_COLD

    def test_security_sentinel_raises_exception(self):
        guard = RavenGuard(ledger=InMemoryLedger())
        security_policy = create_security_sentinel_policy()

        # Security sentinel has zero tolerance (threshold_strike=60, raise_on_strike=True)
        with pytest.raises(RavenStrikeException) as excinfo:
            guard.process_turn("attacker_99", "Lu goblok banget sih!", policy=security_policy)

        assert "Security Sentinel Alert" in str(excinfo.value)

