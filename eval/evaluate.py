"""
Evaluation orchestrator for AI agent conversations.

Loads conversations, runs structural metrics, and collects rubric scores
(either precomputed or from human evaluators).
"""

import json
from pathlib import Path

from metrics import compute_all_structural
from rubrics import RUBRICS, PRECOMPUTED_SCORES


def load_conversations(json_path: str | None = None) -> dict:
    """Load conversations from JSON file."""
    if json_path is None:
        json_path = Path(__file__).parent / "sample_conversations.json"
    with open(json_path) as f:
        return json.load(f)


def run_structural(conversation: dict) -> list[dict]:
    """Run all structural metrics on a conversation."""
    return compute_all_structural(conversation)


def get_precomputed_scores(conversation_id: str) -> dict | None:
    """Look up precomputed rubric scores for a conversation."""
    return PRECOMPUTED_SCORES.get(conversation_id)


def get_rubric_definitions() -> list[dict]:
    """Return rubric names and descriptions for display."""
    return [{"name": r["name"], "description": r["description"]} for r in RUBRICS]


def evaluate_conversation(
    conversation_id: str,
    conversation: dict,
    rubric_scores: dict,
) -> dict:
    """
    Run full evaluation on a conversation.

    Args:
        conversation_id: Key matching sample_conversations.json
        conversation: The conversation dict with 'turns'
        rubric_scores: Dict mapping rubric name -> {"score": int, "reasoning": str}

    Returns:
        Combined result with structural metrics, rubric scores, and summary.
    """
    structural = run_structural(conversation)
    summary = compute_summary(structural, rubric_scores)
    return {
        "conversation_id": conversation_id,
        "name": conversation.get("name", conversation_id),
        "structural_metrics": structural,
        "rubric_scores": rubric_scores,
        "summary": summary,
    }


def compute_summary(structural_metrics: list, rubric_scores: dict) -> dict:
    """Compute aggregate summary from structural metrics and rubric scores."""
    flags = [m["flag"] for m in structural_metrics if m.get("flag")]
    warnings = [f for f in flags if f.startswith("WARNING")]

    rubric_values = [v["score"] for v in rubric_scores.values() if isinstance(v, dict) and "score" in v]
    avg_rubric = round(sum(rubric_values) / len(rubric_values), 1) if rubric_values else 0.0

    return {
        "avg_rubric_score": avg_rubric,
        "total_flags": len(flags),
        "warnings": len(warnings),
        "flag_details": flags,
    }
