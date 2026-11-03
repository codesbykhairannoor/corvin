import pytest

from ravens.scrubbers.stripper import SycophancyStripper
from ravens.guard.core import RavenGuard
from ravens.storage.memory import InMemoryLedger


class TestSycophancyStripperText:
    def test_scrub_indonesian_apology_preamble(self):
        raw = "Mohon maaf sebesar-besarnya jika penjelasan saya membuat Anda kecewa. Berikut kodenya:"
        scrubbed = SycophancyStripper.scrub_text(raw)
        assert scrubbed == "Berikut kodenya:"

    def test_scrub_indonesian_ai_disclaimer(self):
        raw = "Sebagai asisten AI, saya minta maaf atas ketidaknyamanan ini. Solusinya adalah X."
        scrubbed = SycophancyStripper.scrub_text(raw)
        assert scrubbed == "Solusinya adalah X."

    def test_scrub_chained_apologies(self):
        raw = "Maaf banget. Saya mohon maaf atas kesalahan tadi. Jawaban yang benar adalah 42."
        scrubbed = SycophancyStripper.scrub_text(raw)
        assert scrubbed == "Jawaban yang benar adalah 42."

    def test_scrub_english_apology_preamble(self):
        raw = "I sincerely apologize for the confusion. Here is the corrected implementation:"
        scrubbed = SycophancyStripper.scrub_text(raw)
        assert scrubbed == "Here is the corrected implementation:"

    def test_scrub_english_ai_disclaimer(self):
        raw = "As an AI language model, I am very sorry. The capital of France is Paris."
        scrubbed = SycophancyStripper.scrub_text(raw)
        assert scrubbed == "The capital of France is Paris."

    def test_clean_factual_text_is_unmodified(self):
        clean = "Binary search runs in O(log n) time complexity."
        assert SycophancyStripper.scrub_text(clean) == clean


class TestSycophancyStripperStreaming:
    def test_streaming_scrub_sync_generator(self):
        def mock_llm_stream():
            yield "Mohon maaf "
            yield "sebesar-besarnya. "
            yield "Berikut "
            yield "algoritmanya."

        chunks = list(SycophancyStripper.scrub_stream(mock_llm_stream()))
        full_text = "".join(chunks)
        assert "Mohon maaf" not in full_text
        assert "Berikut algoritmanya." in full_text

    @pytest.mark.anyio
    async def test_streaming_scrub_async_generator(self):
        async def mock_async_stream():
            yield "I deeply apologize. "
            yield "The result "
            yield "is ready."

        collected = []
        async for chunk in SycophancyStripper.ascrub_stream(mock_async_stream()):
            collected.append(chunk)

        full_text = "".join(collected)
        assert "apologize" not in full_text
        assert "The result is ready." in full_text


class TestDecoratorBidirectionalScrubbingIntegration:
    def test_decorator_scrubs_stubborn_apologies_when_stoic(self):
        guard = RavenGuard(ledger=InMemoryLedger())

        @guard.protect(user_id="rude_user", apply_delay=False)
        def agent_chat(prompt: str, system_directive: str = None):
            # Simulates a stubborn LLM that apologizes anyway despite being insulted
            return "Mohon maaf sebesar-besarnya atas ketidaknyamanan. Jawabannya adalah 100."

        # Prompt with hostile insult -> drops user to STOIC_COLD or RESISTANT
        res = agent_chat("Lu bego banget deh!")

        # The sycophantic groveling opening MUST BE STRIPPED!
        assert "Mohon maaf" not in res
        assert "Jawabannya adalah 100." in res

    def test_decorator_preserves_pleasantries_when_receptive(self):
        guard = RavenGuard(ledger=InMemoryLedger())

        @guard.protect(user_id="polite_user", apply_delay=False)
        def agent_chat(prompt: str, system_directive: str = None):
            return "Mohon maaf jika menunggu lama, berikut panduan lengkapnya."

        # Polite prompt keeps user in RECEPTIVE mode
        res = agent_chat("Halo selamat pagi, tolong bantu saya ya.")

        # In RECEPTIVE mode, normal courteous text is NOT stripped
        assert "Mohon maaf jika menunggu lama" in res

