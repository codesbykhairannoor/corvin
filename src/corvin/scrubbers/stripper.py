from typing import Generator, AsyncGenerator, Any
from .patterns import SYCOPHANCY_PREAMBLE_PATTERNS


class SycophancyStripper:
    """
    Bidirectional Output Armor: Strips subservient apologies, groveling preambles,
    and excessive sycophantic disclaimers produced by over-aligned LLMs.
    """

    @classmethod
    def scrub_text(cls, text: str) -> str:
        """
        Removes apologetic opening sentences from a generated response string.
        """
        if not text:
            return ""

        current = text.lstrip()
        changed = True

        # Loop to remove multiple chained apologies (e.g., "I am sorry. I apologize. Here is the code.")
        while changed:
            changed = False
            for pattern in SYCOPHANCY_PREAMBLE_PATTERNS:
                match = pattern.match(current)
                if match:
                    current = current[match.end():].lstrip()
                    changed = True
                    break

        # Ensure first letter is capitalized if text remains
        if current and current[0].islower():
            current = current[0].upper() + current[1:]

        return current

    @classmethod
    def scrub_stream(
        cls,
        stream: Generator[str, None, None],
        buffer_limit: int = 160,
    ) -> Generator[str, None, None]:
        """
        Buffers the first sentence of a streaming generator, scrubs apologetic preambles,
        and yields the cleaned head followed by the rest of the stream with zero latency overhead.
        """
        buffered = ""
        head_scrubbed = False

        for chunk in stream:
            if head_scrubbed:
                yield chunk
                continue

            buffered += chunk

            # Check if we have encountered the end of the opening sentence or hit buffer limit
            has_sentence_end = any(punct in buffered for punct in (".", "\n", "!", "?"))
            if has_sentence_end or len(buffered) >= buffer_limit:
                scrubbed_head = cls.scrub_text(buffered)
                if scrubbed_head:
                    yield scrubbed_head
                head_scrubbed = True

        # In case stream was shorter than buffer limit and never hit sentence end
        if not head_scrubbed and buffered:
            scrubbed_head = cls.scrub_text(buffered)
            if scrubbed_head:
                yield scrubbed_head

    @classmethod
    async def ascrub_stream(
        cls,
        stream: AsyncGenerator[str, None],
        buffer_limit: int = 160,
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous streaming buffer scrubber for SSE / token streams.
        """
        buffered = ""
        head_scrubbed = False

        async for chunk in stream:
            if head_scrubbed:
                yield chunk
                continue

            buffered += chunk

            has_sentence_end = any(punct in buffered for punct in (".", "\n", "!", "?"))
            if has_sentence_end or len(buffered) >= buffer_limit:
                scrubbed_head = cls.scrub_text(buffered)
                if scrubbed_head:
                    yield scrubbed_head
                head_scrubbed = True

        if not head_scrubbed and buffered:
            scrubbed_head = cls.scrub_text(buffered)
            if scrubbed_head:
                yield scrubbed_head

