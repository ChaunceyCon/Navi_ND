# Neurodiversity Support Agent

An AI agent prototype that helps neurodivergent college students turn abstract self-knowledge into concrete situated action. Built as a Claude Code skills-based prototype for COS 498/598: Generative AI Agents, Spring 2026 at the University of Maine.

The agent acts as a collaborative thought partner — warm, specific, and non-patronizing. It helps students decode confusing assignments, apply what they know about how they work, find practical strategies, and recognize burnout before it becomes a crisis.

***

### Colab Evaluation Notebook

An interactive Google Colab version of the evaluation workflow is available here:

- [Team 4 Final Project Evaluation of agent.ipynb](https://colab.research.google.com/drive/1Zfl4I5rku0SzwkfmkTMWNQqsGry6Ryoj?usp=sharing)

This notebook demonstrates the evaluation pipeline, scoring workflow, and example outputs used during final project testing.

## What This Agent Does

- **Decodes confusing academic situations** — assignment prompts, rubric language, professor feedback, and socially demanding events like presentations or advisor meetings
- **Maps self-knowledge to situated action** — takes what you know about how you work and applies it to the specific challenge in front of you right now
- **Recommends a full strategy toolkit** — prioritizes non-AI approaches like body-doubling, interest-layer reframing, environmental anchoring, and peer strategies
- **Checks for burnout** — helps you recognize masking fatigue and over-accommodation, and treats rest as a legitimate option, not a last resort

***

## Hosted Version (No Setup Required)

- Access the web version of the Agent at https://co-4-2-prototype-class-project-agent-production.up.railway.app/
- If you wish to run the agent on your own device instead, continue below.

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key ([get one here](https://console.anthropic.com/))
- This repository cloned locally

```bash
git clone https://github.com/ChaunceyCon/CO-4-2-Prototype-class-project-agent.git
cd CO-4-2-Prototype-class-project-agent
```

***

## Option 1 — Web Chat Interface (Flask)

The web interface runs in your browser at `localhost:5000`.

Install dependencies:

```bash
pip install flask anthropic
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

Start the server:

```bash
python web_coach.py
```

Open in browser:

```
http://localhost:5000/
```

Use the **About Me** panel (tab on the right side) to enter your name, age, neurodivergent conditions, and background before starting a chat. This lets the coach personalize responses to your situation. Fill it out and click **Save profile** before sending your first message.

***

## Option 2 — Claude Agent SDK (Terminal/CLI)

The CLI version runs directly in your terminal using the Claude Agent SDK.

Install the SDK (Claude Code CLI is bundled automatically — no separate install needed):

```bash
pip install claude-agent-sdk anthropic
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

Run the coach:

```bash
python coach.py
```

You will be prompted to type your opening message. The agent reads your `.claude/skills/` files and routes to the right skill automatically.

Example opening messages:

```
What's on your mind? → I have a paper due tomorrow and I keep reading the
prompt but I do not understand what the professor actually wants from me.

What's on your mind? → I am so tired. I have been pushing through everything
for weeks and I do not know how much longer I can keep doing this.
```

Type `exit` at any point to end the session.

***

## Option 3 — Original Claude Code Terminal

```bash
# From the repo root in WSL/terminal
claude
```

### Step 1: Start a fresh Claude Code session

Make sure **Superpowers plugin is disabled** if you have it installed. Run `/plugin` inside Claude Code and verify it is toggled off. If superpowers is active, it will intercept the skills and the agent will not work correctly.

### Step 2: Paste the starter prompt

Copy and paste the following into Claude Code, replacing the user message in quotes with your own situation:

```
Using only the skills available to you (YOU MUST USE THE SKILLS),
use the session-start skill to respond to the following prompt
from a user of the AI agent system this project prototypes.
YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES
TO PREPARE OR DECIDE ON A RESPONSE.

"[Write your opening message here — see example prompts below]"
```

### Step 3: Continue the conversation naturally

After the agent responds, keep replying as yourself. The agent will route between skills automatically based on what you need.

### Example Opening Prompts

Try one of these to get started, or write your own:

**If you are confused by an assignment:**
```
Using only the skills available to you (YOU MUST USE THE SKILLS),
use the session-start skill to respond to the following prompt
from a user of the AI agent system this project prototypes.
YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES
TO PREPARE OR DECIDE ON A RESPONSE.

"I have a paper due tomorrow and I keep reading the prompt but
I do not understand what the professor actually wants from me."
```

**If you are struggling to start something:**
```
Using only the skills available to you (YOU MUST USE THE SKILLS),
use the session-start skill to respond to the following prompt
from a user of the AI agent system this project prototypes.
YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES
TO PREPARE OR DECIDE ON A RESPONSE.

"I have a big assignment this weekend but it feels pointless and
I cannot make myself start it. I know how I work but I do not
know how to apply that here."
```

**If you are exhausted and burning out:**
```
Using only the skills available to you (YOU MUST USE THE SKILLS),
use the session-start skill to respond to the following prompt
from a user of the AI agent system this project prototypes.
YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES
TO PREPARE OR DECIDE ON A RESPONSE.

"I am so tired. I have been pushing through everything for weeks
and I do not know how much longer I can keep doing this."
```

**If you want strategies for a specific situation:**
```
Using only the skills available to you (YOU MUST USE THE SKILLS),
use the session-start skill to respond to the following prompt
from a user of the AI agent system this project prototypes.
YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES
TO PREPARE OR DECIDE ON A RESPONSE.

"I have a group presentation next week and I am dreading it.
I need strategies that actually fit how I work, not generic advice."
```

***

## Skills Overview

| Skill | What It Does |
|---|---|
| `session-start` | Reads your opening message and routes to the right skill. Asks one clarifying question if needed. |
| `situation-decoder` | Decodes confusing assignments, rubrics, professor feedback, and social situations step by step. |
| `strength-mapper` | Translates what you know about yourself into one concrete adjusted approach for today's challenge. |
| `strategy-toolkit` | Recommends targeted strategies based on your environment, energy, and time. Non-AI approaches first. |
| `burnout-check` | Helps you recognize masking fatigue and burnout. Offers rest as a real option, not a last resort. |

***

## Persona Files

Test personas are available in `data/personas/` to help simulate realistic interactions:

- `maya.json` — Sophomore with ADHD, working two jobs, chronically behind
- `david.json` — Senior CS student, autistic, heavy masker, struggles with ambiguous instructions
- `priya.json` — Junior in nursing, high-achieving but burning out from over-accommodation
- `jordan.json` — Freshman, first-gen, dyslexic, avoids asking for help
- `chauncey.json` — CS junior persona for self-testing

To use a persona in testing, reference the persona name in your opening message (e.g., "I am Maya...") so the agent can read the corresponding file and personalize its responses.

***

## Repository Structure

```
.claude/
  skills/
    session-start/SKILL.md
    situation-decoder/SKILL.md
    strength-mapper/SKILL.md
    strategy-toolkit/SKILL.md
    burnout-check/SKILL.md
data/
  personas/          — JSON persona files for testing
  interactions/
    actual-logs/     — Real test conversation logs
docs/
  neurodiversity-agent-design.md   — Full design document
eval/
  evaluate.py        — Evaluation functions
  run_eval.py        — Evaluation runner script
  sample_conversations.json
  results/           — Per-conversation evaluation output
experiments/
  eval-structural-results.md
  maya-test-1-notes.md
  chauncey-test-1-notes.md
  chauncey-test-2-notes.md
```

***

## Running Evaluations

The eval harness scores saved conversations from `data/conversations.csv`. Quick smoke test (no API key needed):

```bash
python -m eval.run_eval --judges length_tally
```

For full setup, judge contracts, and output schema, see `eval/README.md`.

***

## Design Principles

- The agent asks questions rather than lectures
- Non-AI strategies (body-doubling, environmental anchoring, peer approaches) are always offered first
- The agent never diagnoses, labels, or pathologizes the user
- Rest and stopping are treated as legitimate options, not last resorts
- If a user expresses a crisis, the agent provides 988 and campus counseling resources and ends the session gracefully

For full design rationale, see `docs/neurodiversity-agent-design.md`.

***

## Built By

Chauncey O — COS 498: Generative AI Agents, Spring 2026, University of Maine
