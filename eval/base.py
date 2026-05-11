"""Foundation types for LLM-as-a-judge metrics.

Subclass BaseJudge and implement judge() to add a metric.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Judgment:
    score: Any | None
    reasoning: str
    score_type: str
    judge_name: str
    conversation_id: str
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


class BaseJudge(ABC):
    """Abstract judge. Each subclass implements one metric."""

    name: str = "base"
    score_type: str = "boolean"

    @abstractmethod
    def judge(self, conversation_id: str, transcript: list[dict]) -> Judgment:
        """transcript is a list of {"speaker": str, "text": str} dicts in order."""
        ...
