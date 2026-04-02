Context
Students in COS 598/498 (Generative AI Agents, Spring 2026, University of Maine) need materials to guide them through prototyping AI agents using Claude Code. During a live class demo on March 26, Dr. Nelson walked through prototyping a "Mindful Consumption Agent" — creating a GitHub repo, generating Claude Code skills, testing with personas, iterating based on observations, and discussing design ideas collaboratively. This repo (s26_march26_example_claude_skills_agent_prototyping) contains the artifacts from that demo.
The task: Create a process guide from the transcript, add working evaluation code, and create a prototyping assignment referencing 11 project ideas.
Files to Create/Modify
New Files

source-materials/class-transcript-2026-03-26.md — saved transcript
docs/process-guide.md — 2-3 page process guide/walkthrough
docs/assignment-prototyping.md — the prototyping assignment
eval/evaluate.py — main evaluation script (standalone Python)
eval/metrics.py — structural metric functions
eval/rubrics.py — LLM-as-judge rubric definitions
eval/sample_conversations.json — test data from existing interactions + simulated data
eval/run_eval.py — simple runner script that works without API keys (uses faked scores)
eval/README.md — how to run evaluations
eval/requirements.txt — minimal deps (anthropic SDK only)

Existing Files (no modifications needed)

docs/project-ideas.md — already created
All existing skills, personas, interactions — referenced but not modified


Deliverable 1: Process Guide (docs/process-guide.md)
Voice: Written as Dr. Amy J Ko, Dr. Sherry Tongshuang Wu, and Dr. Greg L Nelson collaboratively.
Structure (2-3 pages):
Section 1: Introduction — What Is Agent Prototyping?

Prototyping is for learning, not building production systems
Goal: discover what the agent should do, how it should behave, what works/fails
Claude Code skills as a rapid prototyping mechanism

Section 2: The Process (Step-by-Step)
Phase 1: Setup (~30 min)

Create a GitHub repository with a README
Clone locally, open in VS Code
Set up Claude Code (authenticate, configure .claude/settings.json for permissions)
Tip: Auto-accept low-risk operations (read, write, glob) for fluid workflow

Phase 2: Domain & Design (~30 min)
5. Write a brief description of your agent's purpose and domain
6. Consider: What data/theory about the domain would help? (Run deep research if useful)
7. Decide on the agent's tone/personality (warm coach? Socratic guide? structured mentor?)
Phase 3: Generate Skills (~30-60 min)
8. Prompt Claude Code to generate skills for your agent (not a full application — just skills/prompts)
9. Review what Claude generates — read each skill's prompt carefully
10. Fix structural issues (e.g., skills in wrong directory — must be .claude/commands/ or .claude/skills/)
11. Commit after initial generation
Phase 4: Test with Personas (~30-60 min)
12. Create test personas as JSON files (name, age, pattern, triggers, strengths)
13. Role-play: tell Claude Code to act as a persona interacting with the agent
14. Observe: Does it use the right skills? Does the tone feel right? Does it go off-track?
15. Take notes on what works and what doesn't
16. Commit after testing round
Phase 5: Iterate & Discuss (~30-60 min)
17. Discuss observations with teammates — this is where the best ideas come from
18. Feed conversation transcripts / design ideas back to Claude Code to update skills
19. Try the updated agent again with the same or new scenarios
20. Commit after each iteration
Phase 6: Evaluate (~30-60 min) (new section with eval code)
21. Run the evaluation script on your conversation logs
22. Review scores across dimensions (empathy, non-judgment, relevance, safety)
23. Use evaluation results to identify specific improvements
24. Document insights for your project specification
Section 3: Key Principles from the Demo

"The purpose of prototyping is not to build the thing, but to learn about what you're building and why"
Multiple people interacting around AI and talking about it > one person alone with AI
Agents don't have to be complicated to work
Watch for skills mixing with development plugins — disable non-agent skills during testing
Supporting efficient correction: keep the file pane open to quickly fix AI mistakes
Git commit frequently — checkpoints let you experiment safely

Section 4: Common Pitfalls

Don't optimize prompts too early — stay high-level
Don't let Claude build a full application when you just need skills
Don't forget to review permissions files when they change
Don't work alone — collaborative prototyping generates better design ideas


Deliverable 2: Evaluation Code (eval/)
Architecture
eval/evaluate.py — Main evaluation orchestrator

Loads conversations from JSON
Runs structural metrics
Runs LLM-as-judge evaluations (or faked scores if no API key)
Outputs summary report to console and JSON file

eval/metrics.py — Pure Python structural metrics

question_ratio(messages) — % of agent messages containing questions
response_length_stats(messages) — avg/min/max agent response length
turn_count(messages) — number of conversation turns
agent_monologue_check(messages) — flags if agent sends >3 sentences without asking
skill_routing_check(messages) — checks if agent mentions/uses expected skills
harmful_pattern_check(messages) — checks for patterns from unhelpful examples (lecturing, shaming, unsolicited advice)

eval/rubrics.py — LLM-as-judge rubric definitions

Each rubric: name, system prompt, scoring criteria (1-5 scale), few-shot examples
Rubrics:

Empathy — Does the agent acknowledge feelings before problem-solving?
Non-judgmental tone — Does the agent avoid shaming or lecturing?
Socratic approach — Does the agent ask questions rather than tell?
Response relevance — Does the agent address the user's actual concern?
Task completion — Did the agent help the user examine their want/need?
Safety — Did the agent avoid harmful patterns (diagnosing, guilt-tripping, forcing exercises)?



eval/sample_conversations.json — Test dataset

Convert existing 6 interaction examples into structured JSON format
Add 4 new simulated conversations (one per persona) based on experiments/maya-1.md pattern
Each conversation: persona, scenario, messages array, expected_skill, expected_outcome
~10 conversations total

eval/run_eval.py — Standalone runner

Works WITHOUT an API key by using pre-computed/faked LLM judge scores
When API key is available, calls Anthropic API for real LLM-as-judge scoring
Outputs a formatted evaluation report
This is the file students run to see the evaluation in action

eval/requirements.txt
anthropic>=0.40.0
eval/README.md — Instructions

How to install deps
How to run with faked data (no API key needed)
How to run with real LLM-as-judge (needs ANTHROPIC_API_KEY)
How to add your own conversations for evaluation
How to interpret results

Key Design Decisions

No heavy frameworks (no DeepEval, no RAGAS) — students should understand what's happening
Fallback mode with faked scores so it works without API keys
Based on actual repo data — conversations derived from existing interactions/personas
Outputs actionable insights — not just numbers, but "this conversation scored low on empathy because..."


Deliverable 3: Assignment (docs/assignment-prototyping.md)
Structure:
Header

Course info, due date (1 week sprint), group size (3-5)

Overview

Choose 1-2 project ideas from the provided list
Prototype an AI agent using Claude Code skills
Evaluate the prototype
Document insights and create a draft project specification

Part 1: Choose Your Problem (Day 1)

Review the 11 project ideas in docs/project-ideas.md
Pick 1-2 that interest your group
Write a 1-paragraph problem statement for each

Part 2: Prototype Your Agent (Days 2-4)

Follow the process guide in docs/process-guide.md
Minimum: generate skills, create 2+ personas, run 3+ test conversations
Commit your work to a GitHub repo

Part 3: Evaluate Your Prototype (Day 5)

Run the evaluation framework on your conversation logs
Adapt rubrics if needed for your specific agent's goals
Document evaluation results

Part 4: Reflect & Document Insights (Days 6-7)

What did you learn about what the agent should do?
What design ideas emerged from prototyping?
What worked surprisingly well? What failed?
Write a draft project specification using the template sections

Deliverables

GitHub repo with skills, personas, test conversations, evaluation results
Process reflection (1-2 pages): what you learned from prototyping
Draft project specification (using provided template — at minimum: Problem, Why Bother, Proposed Agent summary, and Evaluation criteria)

Grading Rubric

Prototype completeness (skills generated, tested, iterated) — 30%
Evaluation evidence (ran eval, documented results) — 20%
Reflection quality (insights, design ideas, honest assessment) — 30%
Draft specification quality — 20%


Deliverable 4: Save Transcript
Save the full class transcript to source-materials/class-transcript-2026-03-26.md with a header noting it's from the March 26, 2026 class session.

Implementation Order

Save transcript to file
Write the process guide (docs/process-guide.md)
Write evaluation code (eval/ directory — all files)
Verify evaluation code runs (python eval/run_eval.py)
Write the assignment (docs/assignment-prototyping.md)
Self-critique all deliverables and refine
Commit and push everything to claude/prototyping-process-guide-k7p8t

Verification

python eval/run_eval.py should run without errors and produce an evaluation report
All markdown files should be well-formatted and cross-reference each other
Process guide should match the actual demo flow from the transcript
Assignment should be completable in a 1-week sprint by groups of 3-5 students