"""
OpenAI Moderation Evaluator: Universal 100+ Languages Free Moderation Endpoint.
Uses the official OpenAI Moderation API (omni-moderation-latest) which is 100% free of charge.
"""

import json
import logging
import os
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

from .base import BaseEvaluator, ToneEvaluation

logger = logging.getLogger("corvin.evaluators.moderation")


class OpenAIModerationEvaluator(BaseEvaluator):
    """
    Universal 100+ Languages Moderation Evaluator.
    
    Connects to the official OpenAI Moderation endpoint (https://api.openai.com/v1/moderations).
    Note: The OpenAI Moderation API is completely FREE ($0.00) and does not consume API credits.
    
    Supported:
    - 100+ global languages natively with deep semantic and contextual understanding.
    - Zero third-party dependencies: Uses standard library urllib.request.
    - Automatic exponential backoff & retry resilience on HTTP 429 (rate limits) and 5xx.
    """

    ENDPOINT = "https://api.openai.com/v1/moderations"
    DEFAULT_MODEL = "omni-moderation-latest"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = 3.0,
        max_retries: int = 1,
        retry_backoff_seconds: float = 0.5,
        mock_handler: Optional[Any] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self._mock_handler = mock_handler

    def evaluate(self, text: str) -> ToneEvaluation:
        text_clean = text.strip()
        if not text_clean:
            return ToneEvaluation(
                raw_text=text,
                lexical_score=0.0,
                shouting_score=0.0,
                directedness_score=0.0,
                contrition_score=0.0,
                semantic_score=0.0,
            )

        # Allow testing via mock handler without real network calls
        if self._mock_handler is not None:
            data = self._mock_handler(text_clean)
            return self._parse_moderation_response(text, data)

        if not self.api_key:
            # If no API key provided, log diagnostic warning and return neutral fallback
            logger.debug(
                "OpenAIModerationEvaluator has no API key set; evaluating to neutral 0.0. "
                "Provide OPENAI_API_KEY to enable universal multi-lingual moderation."
            )
            return ToneEvaluation(
                raw_text=text,
                lexical_score=0.0,
                shouting_score=0.0,
                directedness_score=0.0,
                contrition_score=0.0,
                semantic_score=0.0,
                evaluation_tier="openai_no_key",
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Corvin-Guard-Engine",
        }
        payload = {
            "model": self.model,
            "input": text_clean,
        }

        req = urllib.request.Request(
            self.ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        for attempt in range(1 + self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    parsed = self._parse_moderation_response(text, data)
                    if attempt > 0:
                        parsed.telemetry["retries"] = attempt
                    return parsed
            except urllib.error.HTTPError as err:
                err_body = err.read().decode("utf-8", errors="replace")
                # Retry on 429 (Too Many Requests) or 5xx transient server errors
                if err.code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    retry_after = err.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after and retry_after.isdigit() else self.retry_backoff_seconds * (2 ** attempt)
                    logger.info("OpenAI Moderation HTTP %s, retrying in %.2fs (attempt %d/%d)...", err.code, sleep_time, attempt + 1, self.max_retries)
                    time.sleep(sleep_time)
                    continue

                logger.warning("OpenAI Moderation API HTTP %s error: %s", err.code, err_body)
                return ToneEvaluation(
                    raw_text=text,
                    lexical_score=0.0,
                    shouting_score=0.0,
                    directedness_score=0.0,
                    contrition_score=0.0,
                    semantic_score=0.0,
                    evaluation_tier="openai_http_error",
                    telemetry={"http_status": err.code, "error": err_body, "attempts": attempt + 1},
                )
            except urllib.error.URLError as err:
                # Retry on transient network/DNS failure if attempts remain
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_seconds)
                    continue
                logger.warning("OpenAI Moderation network/DNS error: %s", err.reason)
                return ToneEvaluation(
                    raw_text=text,
                    lexical_score=0.0,
                    shouting_score=0.0,
                    directedness_score=0.0,
                    contrition_score=0.0,
                    semantic_score=0.0,
                    evaluation_tier="openai_network_error",
                    telemetry={"network_error": str(err.reason), "attempts": attempt + 1},
                )
            except Exception as err:
                logger.warning("OpenAI Moderation unexpected error: %s", err)
                return ToneEvaluation(
                    raw_text=text,
                    lexical_score=0.0,
                    shouting_score=0.0,
                    directedness_score=0.0,
                    contrition_score=0.0,
                    semantic_score=0.0,
                    evaluation_tier="openai_exception",
                    telemetry={"error": str(err)},
                )

    def _parse_moderation_response(self, raw_text: str, data: Dict[str, Any]) -> ToneEvaluation:
        results = data.get("results", [])
        if not results:
            return ToneEvaluation(
                raw_text=raw_text,
                lexical_score=0.0,
                shouting_score=0.0,
                directedness_score=0.0,
                contrition_score=0.0,
                semantic_score=0.0,
            )

        result0 = results[0]
        flagged = result0.get("flagged", False)
        scores = result0.get("category_scores", {})
        categories = result0.get("categories", {})

        # Extract max harassment & hate scores
        harassment_score = float(scores.get("harassment", 0.0))
        harassment_threatening = float(scores.get("harassment/threatening", 0.0))
        hate_score = float(scores.get("hate", 0.0))
        hate_threatening = float(scores.get("hate/threatening", 0.0))
        violence_score = float(scores.get("violence", 0.0))
        self_harm_score = float(scores.get("self-harm", 0.0))

        # Max overt toxicity
        lexical_component = max(harassment_score, hate_score)
        # Max severe / existential violence
        semantic_component = max(harassment_threatening, hate_threatening, violence_score, self_harm_score)

        detected_intents: List[str] = [
            cat.upper() for cat, is_active in categories.items() if is_active
        ]

        # Normalize directedness
        directedness = 1.0 if (harassment_score > 0.4 or hate_score > 0.4 or flagged) else 0.0

        return ToneEvaluation(
            raw_text=raw_text,
            lexical_score=min(1.0, lexical_component),
            shouting_score=0.0,
            directedness_score=directedness,
            contrition_score=0.0,
            semantic_score=min(1.0, semantic_component),
            semantic_intents=detected_intents,
        )

