#!/usr/bin/env python3
"""
Mindful Consumption Agent — Evaluation Pipeline

Run this script to evaluate sample agent conversations using:
  1. Structural metrics (automatic — no API key needed)
  2. Rubric scoring (human-in-the-loop OR precomputed)

Usage:
  python eval/run_eval.py                # Interactive mode
  python eval/run_eval.py --precomputed  # Use precomputed scores (no prompts)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure eval/ is on the import path
sys.path.insert(0, str(Path(__file__).parent))

from evaluate import (
    load_conversations,
    run_structural,
    get_precomputed_scores,
    get_rubric_definitions,
    evaluate_conversation,
)


BANNER = """
══════════════════════════════════════════════════════════
  Mindful Consumption Agent — Evaluation Pipeline
  COS 598/498: Generative AI Agents — Spring 2026
══════════════════════════════════════════════════════════
"""


def print_structural(results: list) -> None:
    """Print structural metric results."""
    print("\n  STRUCTURAL METRICS")
    print("  " + "─" * 50)
    for r in results:
        val = r["value"]
        if isinstance(val, dict):
            if "mean" in val:
                val_str = f"mean={val['mean']}, max={val['max']}, long_turns={val['long_turns']}"
            elif "total" in val:
                val_str = f"{val['total']} found"
                if val.get("categories"):
                    val_str += f" ({', '.join(val['categories'].keys())})"
            else:
                val_str = str(val)
        else:
            val_str = str(val)
        print(f"  {r['metric']:<25} {val_str}")

    flags = [r["flag"] for r in results if r.get("flag")]
    if flags:
        print("\n  Flags:")
        for f in flags:
            print(f"    * {f}")
    else:
        print("\n  Flags: (none)")


def print_rubric_scores(scores: dict, source: str) -> None:
    """Print rubric scores."""
    print(f"\n  RUBRIC SCORES ({source})")
    print("  " + "─" * 50)
    total = 0
    count = 0
    for name, data in scores.items():
        score = data["score"]
        reasoning = data.get("reasoning", "")
        print(f"  {name:<25} {score}/5")
        if reasoning:
            print(f"    {reasoning}")
        total += score
        count += 1
    if count > 0:
        print(f"\n  {'Average:':<25} {round(total / count, 1)}/5")


def save_result(conv_id: str, result: dict, output_dir: Path) -> Path:
    """Save a per-conversation evaluation result as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"result-{conv_id}.json"
    path = output_dir / filename
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


def save_summary(all_results: list, output_dir: Path) -> Path:
    """Save the cross-conversation summary as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    summary = {
        "timestamp": timestamp,
        "conversations": [],
    }
    for r in all_results:
        summary["conversations"].append({
            "conversation_id": r["conversation_id"],
            "name": r["name"],
            "source_file": r.get("source_file", ""),
            "avg_rubric_score": r["summary"]["avg_rubric_score"],
            "total_flags": r["summary"]["total_flags"],
            "warnings": r["summary"]["warnings"],
            "flag_details": r["summary"]["flag_details"],
        })
    path = output_dir / f"summary-{timestamp}.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    return path


def collect_human_scores(source_file: str, rubrics: list[dict]) -> dict:
    """Prompt the user to score a conversation on each rubric dimension."""
    print(f"\n  Please open and read this file:")
    print(f"    {source_file}")
    input("\n  Press Enter when you've read the conversation...")

    scores = {}
    print("\n  Score each dimension from 1 (worst) to 5 (best):\n")
    for rubric in rubrics:
        name = rubric["name"]
        desc = rubric["description"]
        print(f"  {name.upper()}: {desc}")
        while True:
            try:
                raw = input(f"    Your score (1-5): ").strip()
                score = int(raw)
                if 1 <= score <= 5:
                    break
                print("    Please enter a number between 1 and 5.")
            except (ValueError, EOFError):
                print("    Please enter a number between 1 and 5.")

        reasoning = input(f"    Brief reasoning (optional, Enter to skip): ").strip()
        scores[name] = {"score": score, "reasoning": reasoning if reasoning else "Human evaluation"}

    return scores


def main():
    parser = argparse.ArgumentParser(description="Evaluate agent conversations")
    parser.add_argument(
        "--precomputed",
        action="store_true",
        help="Use precomputed rubric scores (no interactive prompts)",
    )
    args = parser.parse_args()

    print(BANNER)

    conversations = load_conversations()
    rubrics = get_rubric_definitions()
    all_results = []
    output_dir = Path(__file__).parent / "results"

    for conv_id, conv in conversations.items():
        print(f"\n{'=' * 58}")
        print(f"  EVALUATING: {conv.get('name', conv_id)}")
        print(f"  Persona: {conv.get('persona', 'unknown')}")
        print(f"{'=' * 58}")

        # Structural metrics (always automatic)
        structural = run_structural(conv)
        print_structural(structural)

        # Rubric scores
        if args.precomputed:
            scores = get_precomputed_scores(conv_id)
            if scores:
                print_rubric_scores(scores, "precomputed")
            else:
                print(f"\n  No precomputed scores for '{conv_id}' — skipping rubrics.")
                scores = {}
        else:
            precomputed = get_precomputed_scores(conv_id)
            choice = ""
            while choice not in ("h", "p"):
                choice = input(
                    "\n  Score rubrics yourself [h] or use precomputed [p]? "
                ).strip().lower()
                if not choice:
                    choice = "p"

            if choice == "h":
                scores = collect_human_scores(conv.get("source_file", ""), rubrics)
                print_rubric_scores(scores, "human")
            else:
                scores = precomputed or {}
                if scores:
                    print_rubric_scores(scores, "precomputed")
                else:
                    print(f"\n  No precomputed scores for '{conv_id}'.")

        result = evaluate_conversation(conv_id, conv, scores)
        result["source_file"] = conv.get("source_file", "")
        all_results.append(result)

        # Save per-conversation result
        saved_path = save_result(conv_id, result, output_dir)
        print(f"\n  Saved: {saved_path.relative_to(Path(__file__).parent.parent)}")

    # Final summary
    print(f"\n\n{'═' * 58}")
    print("  SUMMARY ACROSS ALL CONVERSATIONS")
    print(f"{'═' * 58}\n")
    print(f"  {'Conversation':<35} {'Avg Rubric':<12} {'Flags'}")
    print(f"  {'─' * 55}")
    for r in all_results:
        s = r["summary"]
        name = r["name"]
        if len(name) > 33:
            name = name[:30] + "..."
        avg = f"{s['avg_rubric_score']}/5" if s["avg_rubric_score"] else "n/a"
        print(f"  {name:<35} {avg:<12} {s['total_flags']} flags ({s['warnings']} warnings)")

    # Save summary
    summary_path = save_summary(all_results, output_dir)
    print(f"  Results saved to: {output_dir.relative_to(Path(__file__).parent.parent)}/")
    print(f"  Summary: {summary_path.name}")
    print()


if __name__ == "__main__":
    main()
