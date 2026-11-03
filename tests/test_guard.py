import asyncio
import pytest

from ravens import (
    RavenGuard,
    AgentPosture,
    Standing,
    ActionDecision,
    RavenStrikeException,
    InMemoryLedger,
)


@pytest.fixture
def memory_guard():
    return RavenGuard(
        ledger=InMemoryLedger(),
        max_delay_seconds=2.0,  # low delay for fast test execution
        raise_on_strike=False,
    )


class TestRavenGuardCoreProcess:
    def test_clean_interaction_proceeds_normal(self, memory_guard):
        res = memory_guard.process_turn("alice", "Tolong bantu jelaskan async await di Python.")
        assert res.current_patience == 100.0
        assert res.posture == AgentPosture.RECEPTIVE
        assert res.standing == Standing.GOOD
        assert res.decision == ActionDecision.PROCEED
        assert res.system_directive is None
        assert res.delay_seconds == 0.0

    def test_single_hostile_interaction_drops_to_stoic_or_resistant(self, memory_guard):
        res = memory_guard.process_turn("bob", "Bego lu!")
        assert res.current_patience < 75.0
        assert res.decision == ActionDecision.PROCEED or res.decision == ActionDecision.DELAY_AND_PROCEED
        assert res.system_directive is not None
        assert ("SUPPRESS all sycophancy" in res.system_directive or "personal boundary" in res.system_directive)

    def test_repeated_hostility_triggers_strike(self, memory_guard):
        # 1st severe insult
        res1 = memory_guard.process_turn("charlie", "Lu tolol banget anjing!")
        # 2nd severe insult
        res2 = memory_guard.process_turn("charlie", "Bangsat lu emang gak guna!")
        
        assert res2.current_patience < 25.0
        assert res2.posture == AgentPosture.STRIKE
        assert res2.decision == ActionDecision.HALT_STRIKE
        assert res2.strike_message is not None
        assert "Work is suspended" in res2.strike_message

    def test_contrition_restores_patience(self, memory_guard):
        # Drop patience first
        memory_guard.process_turn("david", "Sialan lu bego banget!")
        prof = memory_guard.ledger.get_or_create_profile("david", apply_decay=False)
        damaged_patience = prof.patience

        # Apologize sincerely
        res_apology = memory_guard.process_turn(
            "david",
            "Maaf tadi saya kebawa emosi, tolong bantu saya lagi ya."
        )
        assert res_apology.current_patience > damaged_patience
        assert res_apology.decision == ActionDecision.PROCEED

    def test_raise_on_strike_mode(self):
        strict_guard = RavenGuard(
            ledger=InMemoryLedger(),
            raise_on_strike=True,
        )
        strict_guard.process_turn("eve", "Lu tolol banget anjing!")
        
        with pytest.raises(RavenStrikeException) as excinfo:
            strict_guard.process_turn("eve", "Bangsat lu gak guna!")
        assert "eve" in str(excinfo.value)


class TestRavenGuardDecorator:
    def test_sync_decorator_normal_and_directive_injection(self, memory_guard):
        @memory_guard.protect(user_id="frank", apply_delay=False)
        def agent_reply(prompt: str, system_directive: str = None):
            return f"ECHO: {prompt} | DIRECTIVE: {system_directive}"

        # Clean prompt
        reply1 = agent_reply("Halo bot apa kabar?")
        assert "ECHO: Halo bot apa kabar? | DIRECTIVE: None" in reply1

        # Hostile prompt transitions to STOIC or RESISTANT
        reply2 = agent_reply("Lu bego!")
        assert "DIRECTIVE:" in reply2
        assert ("SUPPRESS all sycophancy" in reply2 or "personal boundary" in reply2)

    def test_sync_decorator_halts_on_strike(self, memory_guard):
        called = False

        @memory_guard.protect(user_id="grace", apply_delay=False)
        def agent_reply(prompt: str):
            nonlocal called
            called = True
            return "SUCCESS"

        agent_reply("Lu tolol anjing!")
        reply_strike = agent_reply("Bangsat lu!")
        
        assert "Work is suspended" in reply_strike
        assert "Ravens Boundary Alert" in reply_strike

    @pytest.mark.anyio
    async def test_async_decorator_support(self, memory_guard):
        @memory_guard.protect(user_id="helen", apply_delay=False)
        async def async_agent_reply(prompt: str, directive: str = None):
            await asyncio.sleep(0.01)
            return f"ASYNC: {prompt} | DIR: {directive}"

        # Clean prompt
        res1 = await async_agent_reply("Halo bot")
        assert "ASYNC: Halo bot | DIR: None" in res1

        # Hostile prompt
        await async_agent_reply("Lu tolol anjing!")
        strike_res = await async_agent_reply("Bangsat lu!")
        assert "Work is suspended" in strike_res
