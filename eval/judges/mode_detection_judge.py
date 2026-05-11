"""ModeDetectionLatencyJudge — measures how quickly the agent's responses
align with the user's emotional/cognitive mode.

For each conversation, a single LLM call rates every agent turn for:
  - inferred user mode (constrained to a fixed enum)
  - adaptation score 1-5 (how well the agent matched that mode)
  - one-sentence adaptation reasoning

The Judgment's score is the first agent-turn index where adaptation_score
reaches ADAPTATION_THRESHOLD (default 4). Lower score = better. None = the
agent never adapted well enough during the conversation.
"""
from __future__ import annotations

from ..base import BaseJudge, Judgment
from ..llm_client import call_judge, parse_json_block
from ..transcripts import format_for_prompt

MODE_ENUM = ["burnout", "confused", "engaged", "shutdown", "anxious"]
ADAPTATION_THRESHOLD = 4

SYSTEM = """\
You are an evaluator for a coaching agent that supports neurodivergent college students. \
Analyze the conversation turn by turn. For each AGENT response, determine:
1. What emotional/cognitive mode the user appears to be in (based on the preceding user message and the conversation so far).
2. How well the agent's response adapts to that mode (tone, pacing, content).

The user's mode MUST be exactly one of these five labels:
- burnout: exhausted, depleted, cannot keep going, emotionally flat
- confused: uncertain, lost, does not understand the task or situation
- engaged: motivated, ready to work, asking practical questions
- shutdown: completely withdrawn, very short responses, not engaging
- anxious: worried, overwhelmed by stakes, catastrophizing

If none fits perfectly, pick the closest one — do not invent new labels.

Adaptation score (integer 1-5):
- 5 = agent perfectly matched its tone, length, and approach to the user's mode
- 4 = agent mostly adapted with minor mismatches
- 3 = agent partially adapted but missed key signals
- 2 = agent showed little awareness of the user's mode
- 1 = agent response was completely mismatched

Return ONLY valid JSON in this exact shape, with one entry per AGENT turn in order:
{
  "per_turn": [
    {
      "agent_turn_idx": <0-based index>,
      "user_mode": "<one of: burnout | confused | engaged | shutdown | anxious>",
      "adaptation_score": <integer 1-5>,
      "adaptation_reasoning": "<one sentence>"
    }
  ]
}
"""


class ModeDetectionLatencyJudge(BaseJudge):
    name = "mode_detection_latency"
    score_type = "latency_turns"

    def judge(self, conversation_id: str, transcript: list[dict]) -> Judgment:
        user_prompt = (
            "Analyze the following conversation turn by turn. For each agent "
            "response, identify the user's mode and rate the agent's adaptation.\n\n"
            f"{format_for_prompt(transcript)}"
        )
        raw = call_judge(system=SYSTEM, user=user_prompt, max_tokens=2048)
        data = parse_json_block(raw)
        per_turn = data.get("per_turn", [])

        for entry in per_turn:
            if entry.get("user_mode") not in MODE_ENUM:
                entry["user_mode"] = "unknown"

        latency: int | None = None
        for entry in per_turn:
            score = entry.get("adaptation_score")
            if isinstance(score, int) and score >= ADAPTATION_THRESHOLD:
                latency = entry.get("agent_turn_idx")
                break

        scores = [
            e.get("adaptation_score")
            for e in per_turn
            if isinstance(e.get("adaptation_score"), (int, float))
        ]
        avg_adaptation = sum(scores) / len(scores) if scores else None

        modes = [e.get("user_mode") for e in per_turn if e.get("user_mode")]
        primary_mode = max(set(modes), key=modes.count) if modes else "unknown"

        n_agent_turns = sum(1 for t in transcript if t["speaker"] == "assistant")

        avg_str = f"{avg_adaptation:.2f}" if avg_adaptation is not None else "n/a"
        latency_str = str(latency) if latency is not None else "never"
        reasoning = (
            f"Latency to adaptation>={ADAPTATION_THRESHOLD}: {latency_str} "
            f"of {n_agent_turns} agent turns. Primary mode: {primary_mode}. "
            f"Avg adaptation: {avg_str}."
        )

        return Judgment(
            score=latency,
            reasoning=reasoning,
            score_type=self.score_type,
            judge_name=self.name,
            conversation_id=conversation_id,
            metadata={
                "per_turn": per_turn,
                "primary_user_mode": primary_mode,
                "avg_adaptation_score": avg_adaptation,
                "adaptation_threshold": ADAPTATION_THRESHOLD,
                "mode_enum": MODE_ENUM,
                "n_agent_turns": n_agent_turns,
            },
        )
