"""Load saved conversations from data/conversations.csv.

The CSV is written by web_coach.py with one row per turn:
    timestamp, session_id, role, content

Each conversation = all rows sharing a session_id, sorted by timestamp.
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_CSV = REPO_ROOT / "data" / "conversations.csv"


def load_transcripts(csv_path: Path = DEFAULT_CSV) -> list[dict]:
    """Return a list of {"id", "path", "turns": [{"speaker", "text"}, ...]}.

    "speaker" is the CSV "role" field (e.g. "user", "assistant").
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No conversations CSV at {csv_path}. "
            "Run web_coach.py to generate one, or download from the deployed app."
        )

    grouped: dict[str, list[dict]] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            grouped.setdefault(row["session_id"], []).append(row)

    transcripts: list[dict] = []
    for session_id, rows in grouped.items():
        rows.sort(key=lambda r: r["timestamp"])
        transcripts.append(
            {
                "id": session_id,
                "path": str(csv_path.relative_to(REPO_ROOT)),
                "turns": [
                    {"speaker": r["role"], "text": r["content"]} for r in rows
                ],
            }
        )

    transcripts.sort(key=lambda t: t["id"])
    return transcripts


def format_for_prompt(transcript: list[dict]) -> str:
    """Format a transcript for inclusion in a judge LLM prompt.

    Numbers user and agent turns separately so a judge can reference
    "AGENT turn 0", "USER turn 1", etc. when returning indices.
    """
    lines: list[str] = []
    user_idx = 0
    agent_idx = 0
    for turn in transcript:
        if turn["speaker"] == "user":
            lines.append(f"[USER turn {user_idx}]\n{turn['text']}")
            user_idx += 1
        else:
            lines.append(f"[AGENT turn {agent_idx}]\n{turn['text']}")
            agent_idx += 1
    return "\n\n".join(lines)
