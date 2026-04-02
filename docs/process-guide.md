# Prototyping AI Agents with Claude Code: A Process Guide
 
**COS 598/498: Generative AI Agents — Spring 2026 — University of Maine**
 
---
 
## What This Guide Is
 
This guide walks you through how to rapidly prototype an AI agent using Claude Code skills. It is based on our live class demo on March 26, 2026, where we built a "Mindful Consumption Agent" from scratch — an agent that helps people examine impulse purchases and find paths to genuine flourishing. The repository from that demo (including all skills, personas, example interactions, and experiment notes) serves as a running example throughout.
 
The goal is not to build a production system. It is to *learn* — about what your agent should do, what it should never do, how people might actually interact with it, and what design decisions matter. You will discover most of this by building something quick and testing it, not by planning in the abstract.
 
## Prerequisites
 
- A GitHub account and basic git comfort
- VS Code with Claude Code extension (or Claude Code CLI)
- An Anthropic API key or Claude Max subscription
- Familiarity with markdown (skills are written in markdown)
 
## The Process
 
### Phase A: Set Up Your Workspace (30 minutes)
 
**Step 1: Create a GitHub repository.** Make a new repo with a README that briefly describes what your agent will do. Don't overthink this — one paragraph is fine. You'll refine it as you learn.
 
**Step 2: Clone and open.** Clone locally, open in VS Code, and start Claude Code in the terminal. Authenticate when prompted — you'll be redirected to a browser to authorize.
 
**Step 3: Configure permissions.** Claude Code needs permission to read, write, and execute in your repo. In `.claude/settings.json`, whitelist the operations you're comfortable with (Bash, Read, Edit, Write, Glob, Grep). During our demo, we auto-approved low-risk file operations so the workflow stayed fluid — you'll want that too. But always review permission changes to `.claude/` itself, and never blindly approve `rm -rf` or similar destructive commands.
 
> **Security note:** For prototyping without sensitive data, Claude Code's built-in sandbox is sufficient. If you're working with real user data, run in a Docker container.
 
### Phase B: Design Your Agent (1–2 hours)
 
Think carefully about what parts you can ask for AI assistance with, how you should write your own ideas down after prompting AI then integrate your ideas and new ideas made from combining and inspired/lateral thinking from what you generated with AI.

**Step 4: Write a plain-English description of your agent.** Who does it help? What problem does it address? What does a successful interaction look like? Put this in a design doc (see `docs/superpowers/specs/2026...` for the example that was completed after class). This description is what Claude Code will use to generate skills, so be specific about tone, approach, and boundaries.
 
In our demo, we described an agent that uses Socratic questioning (not lecturing) to help people examine purchasing impulses, with a warm-coach personality. That specificity — "Socratic, not preachy" — directly shaped the skills Claude generated.
 
**Step 5: Generate skills.** Ask Claude Code to create skills based on your description. Each skill becomes a file at `.claude/skills/<skill-name>/SKILL.md` — a markdown file with YAML frontmatter (name, description) and detailed prompt instructions.
 
For our agent, Claude generated five skills:
- **session-start** — routes the user's intent to the right skill
- **want-examination** — Socratic questioning about a desire to buy
- **reframe** — names advertising/persuasion techniques and offers alternatives
- **flourishing-prompt** — scaled self-care exercises (1, 5, or 10 minutes)
- **gratitude-inventory** — reflection on what's already good
 
> **Expect problems.** Claude may put files in the wrong directory, use the wrong format, or mix in unrelated plugins. During our demo, it placed skills in `skills/` instead of `.claude/skills/`, and an installed plugin interfered with our agent's own skills. Watch what it does and correct it.
 
**Step 6: Review and iterate on skills.** Read every generated skill carefully. Key things to check:
 
- Are the instructions specific enough? "Be empathetic" is vague. "Acknowledge the user's feeling in one sentence before proceeding" is actionable.
- Does each skill have a "Critical Rules" section defining what the agent should *never* do? Without these, the LLM defaults to generic helpful-assistant behavior.
- Is the tone specified concretely? "Conspiratorial, not preachy" (from our reframe skill) beats "be friendly."
- Do skills reference each other correctly for routing/chaining?
 
**Step 7: Create test personas.** Write/generate at least 4 JSON persona files in `data/personas/` representing realistic, diverse users. Each persona should include: name, age, backstory, emotional triggers, existing strengths, and what success looks like. In our demo, we created Maya (impulse buyer under work stress), David (status-driven purchases from imposter syndrome), Priya (scarcity-anxiety hoarding), and Jordan (TikTok-influenced purchasing).

**Step 7.1: Create a test persona that represents YOU as a persona.** You can use this to "prototype the system as yourself using the system" which gives you another perspective, and it's more valid for you to think about how you might actually react using the system. As another dimension for your thinking and iteration as you prototype.
 
Personas are not optional. Without them you will test with yourself only as the user, and also without AI having context about the user which could make a large difference in the quality of the agent and experience.
 
### Phase C: Test and Iterate (1–2 hours)
Examples here are situated in the example agent from class.

**Step 8: Role-play a test conversation.** Start a new Claude Code session and pretend to be one of your personas. Give the agent context ("I am Maya, a 28-year-old UX designer who stress-shops") and an opening message ("I've been feeling down and think I deserve a whole new wardrobe").
 
Watch what happens:
- Did the router skill classify the intent correctly?
- Did the appropriate skill activate?
- Does the agent's tone match your design?
- Does it ask questions or lecture?
 
**Step 9: Take notes on what works and what doesn't.** Save your observations in `experiments/`. During our test with Maya, we noticed the agent went too deep into analyzing feelings when it should have redirected sooner. We also noticed the "Three Good Things" exercise was effective because it's hard for the agent to screw up. These are design insights — they inform what to change.
 
**Step 10: Write example interactions — both good and bad.** Store these in `data/interactions/actual-logs`. 

You should also generate some simulated interactions that don't actually use the skills. Have beneficial examples show what "good" looks like. Have unhelpful examples are equally important — they define the boundary of acceptable behavior. In our repo, the unhelpful examples (preachy lecturing, dismissive shaming, unsolicited advice) directly informed the "Critical Rules" in every skill.
 
> **The unhelpful examples are very helpful and will really help you improve your design.** Writing them forces you to articulate what your agent should NOT do.
 
**Step 11: Iterate on skills.** Feed specific problems back into the skill prompts. After our test, we realized the flourishing-prompt skill needed to push people toward connecting with others, not just doing solo exercises. We wrote an experiment plan (`experiments/maya-1-plan-for-social-connection-suggesting.md`) and updated the skill.
 
**Step 12: Commit frequently.** Each iteration is a checkpoint. Your git history tells the story of your design process — and lets you revert when Claude Code makes things worse.
 
### Phase D: Collaborate and Refine (ongoing)
 
**Step 13: Discuss with your team.** The most valuable design insights in our demo came not from the AI, but from the human conversation. After watching the agent interact with Maya, we talked about what felt right and wrong, and someone suggested: *what if the agent connected you with a friend to do something positive together, instead of just examining the want alone?*
 
That one idea — making it social — was more valuable than any amount of prompt tuning.
 
> **Our hypothesis: prototyping AI agents works better with multiple people.** You need more than one person interacting around AI and talking about it. One person alone will optimize locally. A group will spot the bigger design opportunities.
 
**Step 14: Feed ideas back into skills.** We copy-pasted our Zoom discussion transcript directly into Claude Code and asked it to update the flourishing-prompt skill. The collaborative insight ("exercises should involve other people to overcome inertia") became a concrete skill update with new exercises: "Quick Reach-Out," "The Two-Person Version," "Positive Impulse Swap."
 
### Phase E: Evaluate (1 hour)
 
**Step 15: Record conversations as structured data.** After testing your agent, save conversations in JSON format (see `eval/sample_conversations.json` for the schema). Include conversations that went well, ones that went poorly, and edge cases.
 
**Step 16: Run structural metrics.** Execute `python eval/evaluate.py --structural-only` on your conversation data. This checks quantitative signals: Is your agent monologuing (too many words per turn)? Is it asking questions (question ratio)? Is it acknowledging feelings before giving advice? These numbers make your qualitative observations concrete.
 
**Step 17: Run LLM-as-judge evaluation.** Execute `python eval/evaluate.py` for rubric-based scores on empathy, non-judgmental tone, relevance, task completion, and safety. Adapt the rubrics in `eval/rubrics.py` to match your agent's specific goals. If your agent is a "Neurodiversity Support Agent," you'd replace the consumerism-specific rubrics with ones about affirming neurodivergent strengths.
 
> **Write your bad examples first, then evaluate them.** If your metrics don't flag the bad examples as bad, your metrics need work — not your agent.
 
## Tips from Our Experience
 
1. **Skills should be specific, not generic.** "Ask one question at a time. Wait. Follow the thread." is better than "use Socratic questioning."
2. **Start with 3–5 skills.** A router, 2–3 core interaction skills, and a session closer. You can always add more.
3. **The agent's tone is a design decision.** Document it explicitly in every skill. "Conspiratorial" and "warm coach" produce very different agents.
4. **Personas force you out of your own head.** A 22-year-old TikTok user and a 45-year-old sales manager will break your agent in different ways.
5. **Don't optimize prompts too early.** If you're tweaking word choices in step 2, you're working at the wrong level. First figure out *what the agent should do*, then worry about *how well it does it*.
6. **Prototyping is learning.** The prototype is not the deliverable — the insights are. Document what you learned, what surprised you, and what you'd change.