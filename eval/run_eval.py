"""Run all configured judges over saved conversations.

Usage:
    python -m eval.run_eval
    python -m eval.run_eval --judges stub
    python -m eval.run_eval --csv data/conversations.csv
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .base import BaseJudge
from .judges.context_questions_judge import ContextQuestionsJudge
from .judges.length_tally import LengthTallyJudge
from .judges.mode_detection_judge import ModeDetectionLatencyJudge
from .transcripts import DEFAULT_CSV, load_transcripts

REPO_ROOT = Path(__file__).parent.parent
RESULTS_DIR = REPO_ROOT / "eval" / "results"

ALL_JUDGES: dict[str, type[BaseJudge]] = {
    "length_tally": LengthTallyJudge,
    "mode_detection_latency": ModeDetectionLatencyJudge,
    "context_questions": ContextQuestionsJudge,
}


def run(csv_path: Path, judge_names: list[str]) -> Path:
    transcripts = load_transcripts(csv_path)
    judges = [ALL_JUDGES[n]() for n in judge_names]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    results: list[dict] = []
    for t in transcripts:
        for judge in judges:
            j = judge.judge(t["id"], t["turns"])
            results.append(j.to_dict())
            print(f"  [{judge.name}] {t['id']}: score={j.score}")

    summary = {
        "timestamp": timestamp,
        "csv_path": str(csv_path.relative_to(REPO_ROOT)),
        "judges": judge_names,
        "n_transcripts": len(transcripts),
        "aggregates": _compute_aggregates(results),
        "results": results,
    }
    out = RESULTS_DIR / f"summary-{timestamp}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote {out.relative_to(REPO_ROOT)}")
    return out


def _compute_aggregates(results: list[dict]) -> dict:
    """Per-judge aggregates over a list of Judgment dicts.

    For each judge name: count of judgments, count of null scores, and
    mean/min/max of any numeric scores. Non-numeric scores are ignored.
    """
    by_judge: dict[str, list[dict]] = {}
    for r in results:
        by_judge.setdefault(r["judge_name"], []).append(r)

    aggregates: dict[str, dict] = {}
    for judge_name, judgments in by_judge.items():
        numeric = [
            j["score"]
            for j in judgments
            if isinstance(j["score"], (int, float)) and not isinstance(j["score"], bool)
        ]
        n_null = sum(1 for j in judgments if j["score"] is None)
        agg: dict = {
            "n_judgments": len(judgments),
            "n_null_scores": n_null,
            "n_numeric_scores": len(numeric),
        }
        if numeric:
            agg["mean_score"] = sum(numeric) / len(numeric)
            agg["min_score"] = min(numeric)
            agg["max_score"] = max(numeric)
        aggregates[judge_name] = agg
    return aggregates


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    p.add_argument(
        "--judges",
        nargs="+",
        default=list(ALL_JUDGES.keys()),
        help=f"Subset of: {list(ALL_JUDGES.keys())}",
    )
    args = p.parse_args()

    unknown = [n for n in args.judges if n not in ALL_JUDGES]
    if unknown:
        raise SystemExit(f"Unknown judges: {unknown}. Known: {list(ALL_JUDGES.keys())}")

    run(args.csv, args.judges)


if __name__ == "__main__":
    main()
