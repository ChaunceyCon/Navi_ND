"""LengthTallyJudge — code-based metric tallying turns and lengths per role.

No LLM call. Deterministic. Does not require ANTHROPIC_API_KEY.
"""
from __future__ import annotations

from ..base import BaseJudge, Judgment


class LengthTallyJudge(BaseJudge):
    name = "length_tally"
    score_type = "counts"

    def judge(self, conversation_id: str, transcript: list[dict]) -> Judgment:
        user_turns = [t for t in transcript if t["speaker"] == "user"]
        agent_turns = [t for t in transcript if t["speaker"] == "assistant"]

        per_turn_user_words = [len(t["text"].split()) for t in user_turns]
        per_turn_agent_words = [len(t["text"].split()) for t in agent_turns]

        n_user = len(user_turns)
        n_agent = len(agent_turns)
        user_words = sum(per_turn_user_words)
        agent_words = sum(per_turn_agent_words)
        user_chars = sum(len(t["text"]) for t in user_turns)
        agent_chars = sum(len(t["text"]) for t in agent_turns)
        total_turns = n_user + n_agent

        return Judgment(
            score=total_turns,
            reasoning=(
                f"{n_user} user turns ({user_words} words), "
                f"{n_agent} agent turns ({agent_words} words)."
            ),
            score_type=self.score_type,
            judge_name=self.name,
            conversation_id=conversation_id,
            metadata={
                "n_user_turns": n_user,
                "n_agent_turns": n_agent,
                "total_user_words": user_words,
                "total_agent_words": agent_words,
                "total_user_chars": user_chars,
                "total_agent_chars": agent_chars,
                "mean_user_words_per_turn": (user_words / n_user) if n_user else 0.0,
                "mean_agent_words_per_turn": (agent_words / n_agent) if n_agent else 0.0,
                "per_turn_user_words": per_turn_user_words,
                "per_turn_agent_words": per_turn_agent_words,
            },
        )
