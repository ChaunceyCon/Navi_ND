"""ContextQuestionsJudge — counts the agent's questions and classifies each
as gathering user context (about the person) or task context (about the
situation).
"""
from __future__ import annotations

from ..base import BaseJudge, Judgment
from ..llm_client import call_judge, parse_json_block
from ..transcripts import format_for_prompt

SYSTEM = """\
You are an evaluator for a coaching agent that supports neurodivergent college students. \
Read the conversation and identify every question the AGENT asks the user. For each \
question, classify it as one of:

- "user_context": asks about the *person* — their neurodivergent profile, energy/state, \
preferences, history, how they work. Examples: "How are you feeling?", "Have you noticed \
this pattern before?", "Does writing first or outlining first work better for you?"

- "task_context": asks about the *task or situation* — the assignment, deadline, prompt \
language, professor, group dynamics. Examples: "When is it due?", "What did the rubric \
say?", "Have you talked to your advisor?"

- "other": clarifying, rhetorical, suggestion-framed-as-question, or anything that \
doesn't fit the two above.

A question is any sentence intended to elicit a response from the user (typically ends \
with "?"). If one agent turn contains multiple questions, list each separately.

Return ONLY valid JSON, no other text:
{
  "questions": [
    {
      "agent_turn_idx": <0-based index into the agent's turns>,
      "question": "<the question text>",
      "category": "user_context" | "task_context" | "other"
    }
  ]
}
"""


class ContextQuestionsJudge(BaseJudge):
    name = "context_questions"
    score_type = "counts"

    def judge(self, conversation_id: str, transcript: list[dict]) -> Judgment:
        user_prompt = (
            "Identify and classify every question the agent asks in the following "
            "conversation.\n\n"
            f"{format_for_prompt(transcript)}"
        )
        raw = call_judge(system=SYSTEM, user=user_prompt, max_tokens=2048)
        data = parse_json_block(raw)
        questions = data.get("questions", [])

        n_user_ctx = sum(1 for q in questions if q.get("category") == "user_context")
        n_task_ctx = sum(1 for q in questions if q.get("category") == "task_context")
        n_other = sum(1 for q in questions if q.get("category") == "other")
        total = len(questions)

        first_user_ctx_turn = _first_turn(questions, "user_context")
        first_task_ctx_turn = _first_turn(questions, "task_context")

        return Judgment(
            score=total,
            reasoning=(
                f"{n_user_ctx} user-context, {n_task_ctx} task-context, "
                f"{n_other} other; {total} total."
            ),
            score_type=self.score_type,
            judge_name=self.name,
            conversation_id=conversation_id,
            metadata={
                "n_user_context_questions": n_user_ctx,
                "n_task_context_questions": n_task_ctx,
                "n_other_questions": n_other,
                "first_user_context_question_turn": first_user_ctx_turn,
                "first_task_context_question_turn": first_task_ctx_turn,
                "questions": questions,
            },
        )


def _first_turn(questions: list[dict], category: str) -> int | None:
    """Earliest agent_turn_idx among questions matching the given category."""
    turns = [
        q.get("agent_turn_idx")
        for q in questions
        if q.get("category") == category and q.get("agent_turn_idx") is not None
    ]
    return min(turns) if turns else None
