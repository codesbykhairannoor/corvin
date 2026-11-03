import asyncio
import time
import pytest

from ravens import (
    RavenGuard,
    InMemoryLedger,
    StreamInterceptor,
    create_free_tier_policy,
)


@pytest.fixture
def stream_guard():
    return RavenGuard(ledger=InMemoryLedger())


class TestSyncStreamingArmor:
    def test_sync_stream_normal_flow(self, stream_guard):
        called = False

        @stream_guard.protect_stream(user_id="stream_user_1", apply_delay=False)
        def generate_tokens(prompt: str, system_directive: str = None):
            nonlocal called
            called = True
            yield "Hello "
            yield "world!"

        chunks = list(generate_tokens("Tolong bantu jelaskan stream generator"))
        assert called is True
        assert "".join(chunks) == "Hello world!"

    def test_sync_stream_early_abort_on_strike(self, stream_guard):
        llm_invoked = False

        @stream_guard.protect_stream(user_id="toxic_streamer", apply_delay=False)
        def generate_tokens(prompt: str):
            nonlocal llm_invoked
            llm_invoked = True
            yield "Should NEVER be emitted"

        # Drive patience to strike
        stream_guard.process_turn("toxic_streamer", "Lu tolol banget anjing!")
        stream_guard.process_turn("toxic_streamer", "Bangsat lu emang gak guna!")

        # Now call streaming generator
        chunks = list(generate_tokens("Mau lu apa sekarang?"))

        # Underling LLM was NEVER invoked (100% compute savings)
        assert llm_invoked is False
        full_output = "".join(chunks)
        assert "Work is suspended" in full_output
        assert "Ravens Boundary Alert" in full_output


class TestAsyncStreamingArmor:
    @pytest.mark.anyio
    async def test_async_stream_normal_flow(self, stream_guard):
        called = False

        @stream_guard.protect_stream(user_id="async_stream_1", apply_delay=False)
        async def astream_tokens(prompt: str, directive: str = None):
            nonlocal called
            called = True
            await asyncio.sleep(0.001)
            yield "Async "
            yield "token "
            yield "stream."

        collected = []
        async for chunk in astream_tokens("Halo bot"):
            collected.append(chunk)

        assert called is True
        assert "".join(collected) == "Async token stream."

    @pytest.mark.anyio
    async def test_async_stream_early_abort_zero_compute(self, stream_guard):
        upstream_llm_called = False

        @stream_guard.protect_stream(user_id="toxic_async_user", apply_delay=False)
        async def astream_llm(prompt: str):
            nonlocal upstream_llm_called
            upstream_llm_called = True
            yield "Token from expensive GPU"

        # Escalate to strike
        stream_guard.process_turn("toxic_async_user", "Lu tolol banget anjing!")
        stream_guard.process_turn("toxic_async_user", "Bangsat lu!")

        chunks = []
        async for chunk in astream_llm("Woi jawab!"):
            chunks.append(chunk)

        # Zero upstream GPU tokens burned
        assert upstream_llm_called is False
        assert "Work is suspended" in "".join(chunks)

    def test_invalid_non_generator_function_raises_type_error(self, stream_guard):
        with pytest.raises(TypeError) as excinfo:
            @stream_guard.protect_stream()
            def not_a_generator(prompt: str):
                return "I am a normal string, not using yield"
        assert "generator functions" in str(excinfo.value)

