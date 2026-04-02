# Evaluation Pipeline

Evaluate AI agent conversations using structural metrics and rubric-based scoring.

## Quick Start

```bash
python eval/run_eval.py --precomputed   # Demo mode: no prompts, uses precomputed scores
python eval/run_eval.py                 # Interactive: score conversations yourself
```

No API keys or installs needed. Runs on Python 3.10+ standard library.

## What It Does

1. **Structural metrics** (automatic): Measures question ratio, response length, word ratio, acknowledgment patterns, and harmful pattern detection across 7 metrics.
2. **Rubric scoring** (human-in-the-loop): Asks you to read an interaction log, then score it on 6 dimensions: empathy, non-judgmental tone, Socratic approach, response relevance, task completion, and safety.

In `--precomputed` mode, rubric scores come from pre-evaluated results in `rubrics.py`.

## Adding Your Own Conversations

Add entries to `sample_conversations.json` following this format:

```json
{
  "my-conversation-id": {
    "name": "Description of the conversation",
    "source_file": "path/to/readable/transcript.md",
    "turns": [
      {"role": "user", "content": "User's message"},
      {"role": "agent", "content": "Agent's response"}
    ]
  }
}
```

Then run `python eval/run_eval.py` and choose `[h]` to score it yourself.
