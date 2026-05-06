# Evaluation Harness

An LLM-as-a-judge harness for the Neurodiversity Support Agent. Reads saved conversations from `data/conversations.csv` and runs a configurable set of metric judges over each session, writing a per-run summary JSON.

***

## What's here

| File | Purpose |
|---|---|
| `base.py` | `BaseJudge` ABC + `Judgment` dataclass — the contract every metric implements. |
| `transcripts.py` | Loads `data/conversations.csv`, groups rows by `session_id`, returns one transcript per session. Also exposes `format_for_prompt` for LLM judges. |
| `llm_client.py` | Anthropic SDK wrapper. `call_judge(system=..., user=...) -> str` plus `parse_json_block`. |
| `run_eval.py` | CLI orchestrator. Iterates judges × transcripts and writes a summary JSON with per-conversation results plus per-judge aggregates. |
| `judges/length_tally.py` | Code-based judge. Counts turns and words per role; per-turn breakdowns in metadata. No API call. |
| `judges/mode_detection_judge.py` | LLM judge. Per-turn user mode (constrained enum) + adaptation score 1–5. Score = first turn agent's adaptation reaches threshold. |
| `judges/context_questions_judge.py` | LLM judge. Enumerates every agent question and tags it `user_context` / `task_context` / `other`. |
| `results/` | Per-run `summary-<timestamp>.json` files land here. |

***

## Input data

Conversations come from `data/conversations.csv`, written by `web_coach.py` with one row per turn:

```
timestamp, session_id, role, content
```

Each `session_id` is one conversation; rows are sorted by timestamp into turns. Locally the CSV is populated by chatting with `python web_coach.py`; in production it lives in the Railway volume and can be downloaded via the `/download-conversations` endpoint.

***

## Running

### Set the API key

The eval harness reads `ANTHROPIC_API_KEY` from your shell environment, matching `coach.py` and `web_coach.py`. It does **not** auto-load `.env`.

**PowerShell (Windows):**

```powershell
# Paste the key for the current session
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Or load it (and any other vars) from .env once for the session
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#=][^=]*)\s*=\s*(.*?)\s*$') {
    [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim('"',"'"), 'Process')
  }
}
```

**Bash:**

```bash
export ANTHROPIC_API_KEY=...
# or load .env wholesale:
set -a; source .env; set +a
```

### Run

```bash
# All registered judges
python -m eval.run_eval

# Subset (use the judge's CLI flag — see table below)
python -m eval.run_eval --judges length_tally
python -m eval.run_eval --judges mode_detection_latency context_questions

# Different CSV
python -m eval.run_eval --csv path/to/other.csv
```

`length_tally` is code-based and needs no API key — useful as a smoke test.

### File vs CLI flag

The CLI flag is the judge's `name` attribute (the key in `ALL_JUDGES`), not the file name:

| File | CLI flag |
|---|---|
| `judges/length_tally.py` | `length_tally` |
| `judges/mode_detection_judge.py` | `mode_detection_latency` |
| `judges/context_questions_judge.py` | `context_questions` |

***

## Output format

Each run writes `eval/results/summary-<timestamp>.json`:

```json
{
  "timestamp": "20260501-161447",
  "csv_path": "data/conversations.csv",
  "judges": ["mode_detection_latency", "context_questions"],
  "n_transcripts": 2,
  "aggregates": {
    "<judge_name>": {
      "n_judgments": 2,
      "n_null_scores": 0,
      "n_numeric_scores": 2,
      "mean_score": 0.0,
      "min_score": 0,
      "max_score": 0
    }
  },
  "results": [
    {
      "score": "<judge-specific>",
      "reasoning": "<short text>",
      "score_type": "<judge-specific>",
      "judge_name": "<flag>",
      "conversation_id": "<session_id from CSV>",
      "metadata": { "...judge-specific fields...": null }
    }
  ]
}
```

`results` has one entry per (judge × conversation). `aggregates` summarizes numeric scores across all conversations for each judge.

### Per-judge score semantics

| Judge | `score` means | Direction | Notable metadata |
|---|---|---|---|
| `length_tally` | total turns (user + agent) | descriptive (no direction) | `n_user_turns`, `n_agent_turns`, total/mean words and chars, `per_turn_user_words`, `per_turn_agent_words` |
| `mode_detection_latency` | 0-based agent-turn index where `adaptation_score >= 4` first occurs (`null` if never) | **lower is better** | `per_turn` array with `user_mode`, `adaptation_score`, `adaptation_reasoning` per turn; `avg_adaptation_score`; `primary_user_mode` |
| `context_questions` | total questions the agent asked | descriptive (no direction) | `n_user_context_questions`, `n_task_context_questions`, `n_other_questions`, `first_user_context_question_turn`, `first_task_context_question_turn`, full `questions` list with per-question turn index and category |

For `mode_detection_latency` specifically, the headline number is the score (latency), but the more discriminating signal is usually `metadata.avg_adaptation_score` (mean of the 1–5 ratings across all turns).

***

## Adding a metric

1. Create `eval/judges/<your_metric>.py` with a subclass of `BaseJudge`:

   ```python
   from ..base import BaseJudge, Judgment
   # If your judge calls the LLM:
   from ..llm_client import call_judge, parse_json_block
   from ..transcripts import format_for_prompt


   class MyJudge(BaseJudge):
       name = "my_judge"          # ← this is the CLI flag
       score_type = "counts"      # free-form label

       def judge(self, conversation_id, transcript):
           # ... your logic ...
           return Judgment(
               score=...,
               reasoning="...",
               score_type=self.score_type,
               judge_name=self.name,
               conversation_id=conversation_id,
               metadata={...},
           )
   ```

2. Register it in `ALL_JUDGES` in `run_eval.py`:

   ```python
   from .judges.my_metric import MyJudge

   ALL_JUDGES = {
       ...,
       "my_judge": MyJudge,
   }
   ```

3. Run it:

   ```bash
   python -m eval.run_eval --judges my_judge
   ```

Each turn in `transcript` is `{"speaker": "user" | "assistant", "text": str}`. For LLM judges, `format_for_prompt(transcript)` formats the turn list with stable `[USER turn N]` / `[AGENT turn N]` markers so the model can return turn indices.

***

## Architecture note

The judge is **completely separate from the main agent**. It does not import `coach.py` or `web_coach.py`, does not use the Claude Agent SDK, has no skills or subagents, and does not run the live agent. It only reads saved conversations from the CSV and calls the Anthropic API directly. You can change the judge's model independently of the main agent.
