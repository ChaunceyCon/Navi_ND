"""Thin wrapper over the Anthropic SDK for judge calls.

Judges supply (system, user) prompts; this module handles the API call and
optional JSON extraction. No Claude Agent SDK, no skills — just messages.create.
"""
from __future__ import annotations

import json
import os

from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"

_client: Anthropic | None = None


def _client_singleton() -> Anthropic:
    global _client
    if _client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        _client = Anthropic()
    return _client


def call_judge(
    *,
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> str:
    """Return the assistant's raw text. Caller decides how to parse it."""
    msg = _client_singleton().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def parse_json_block(text: str) -> dict:
    """Extract the first JSON object from a model response."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in response:\n{text}")
    return json.loads(text[start : end + 1])
