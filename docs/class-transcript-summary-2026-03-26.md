# Class Session Transcript: AI Agent Prototyping with Claude Code
 
**COS 598/498: Generative AI Agents — Spring 2026 — University of Maine**
**Date:** March 26, 2026
**Instructor:** Dr. Greg L Nelson

---
 
## Part 1: Class Intro and Voting (~09:32–09:42)
 
Dr. Nelson opens class by presenting options for the session:
1. Continue the lecture on agent design/evaluation framework
2. Review project ideas and express interest
3. Live demo: using Claude Code to prototype an agent with skills
 
Students vote using emoji reactions. Results: strong interest in both the project ideas review and the live Claude Code demo. Dr. Nelson decides to briefly cover remaining lecture material, quickly review the project ideas, and then do the live Claude Code prototyping.
 
## Part 2: Agent Design Framework — Interaction Design (~09:42–10:14)
 
### Key Concepts Covered:
 
**Mixed-Initiative Collaboration:**
- AI agents should not just use chat sequences where the agent does a bunch of work and the user responds after
- Instead: the agent makes a plan, the user decides which parts should be done by people vs. agents, then they collaborate step-by-step
- The user can click on a step, review/modify the agent's work, then the agent continues executing forward
- Referenced a preprint demonstrating this approach
 
**Custom UI Generation:**
- Agents can generate custom UIs for each step (not just text)
- Works by having a library of UI elements with text-based representations that the AI outputs, which are then deterministically transformed into working UIs
 
**Designing for AI Errors — Core Heuristics:**
- **Efficient invocation:** Making it easy to trigger the agent (e.g., @mentioning in any text box)
- **Efficient dismissal:** Easy to undo/stop unwanted agent actions
- **Efficient correction:** The agent did roughly what you wanted but made mistakes — make it easy to fix (e.g., "Edit Details" link on a suggested calendar event)
- **Scope the service:** When in doubt, don't let the agent try to do too much
- **Explain reasoning:** Show why the system did what it did so users can understand errors and recover
 
**Example: Google Calendar Event Detection**
- An email mentions "Saturday at 1PM" — the AI detects a potential event
- The AI incorrectly interprets "that Saturday" as the upcoming Saturday (Aug 25) instead of the stated date (Dec 29)
- Key insight: some errors are harder to notice than others
- The interface provides an "Edit Details" link = efficient correction
- Without that link, user would have to manually create the event = frustrating
 
**Setting User Expectations:**
- Be upfront about model performance ("detects meetings ~50% of the time")
- Give multiple options (e.g., Gmail's 3 suggested replies — choosing feels better than the AI auto-drafting a single reply)
 
**Process Transparency and Verification:**
- Process transparency: showing what the system is doing step-by-step
- Example: AI2's open-source deep research system — shows query processing, passage retrieval counts, re-ranking, extraction, and generation steps
- Verification support: citations with hover-to-preview, click-to-jump-to-PDF
- Chain of thought: useful but not 100% reliable indicator of actual system behavior
 
**Types of Attribution:**
- Direct quotes (fastest to verify, most words)
- Paraphrasing
- Interpretation
- Different verification time costs for each
 
**Trust and Explanations:**
- If AI is better than humans at the task: explanations increase reliance → increased performance
- If humans are better: explanations can lead to over-reliance
- Framing explanations as verification aids helps in both cases
 
**Evolution Over Time:**
- System learning can be helpful but also disruptive
- Pure implicit feedback (e.g., time spent looking at content) is dangerous
- Make signals explicit — e.g., Claude's editable memory feature
- Provide explicit feedback mechanisms (e.g., running app's "How was this run?" with quick reaction buttons)
- Show consequences of feedback ("We'll try to generate runs that are more interesting")
 
**Global Control:**
- Users need mechanisms to control error tradeoffs
- How much recommendation vs. what you asked for
 
**Using Logs for Improvement:**
- If users edit AI output in the same app, those edits become training data
- Interpretation matters: not all edits mean the AI was wrong (e.g., user changing an ethical position)
- Domain-specific interpretation of edit signals is critical
 
### Takeaways from Lecture:
- Task delegation is the core feature of human-AI collaboration
- Depends on: AI capabilities, human preferences, learning frictions
- Consider before, during, and after the interaction
- General-purpose models enable creativity in measurement — use LLMs to create noisy-but-useful metrics from logs
- Even noisy metrics can steer systems away from bad regions
 
## Part 3: Live Claude Code Prototyping Demo (~10:14–11:36)
 
### Setup Phase
 
1. **Created a GitHub repository** — a blank repo with just a README
2. **Decided on TypeScript** as the language (instructor's recent preference, but noted students should think about libraries first)
3. **Kicked off a deep research report** in the background — searching for existing tools, data sources, libraries, and existing AI agents relevant to the chosen project idea
4. **Cloned the repo locally** and opened in VS Code
5. **Authenticated Claude Code** — went through the OAuth flow, authorized the $20/month account
6. **Configured permissions** — copied a `.claude` permissions file from another project. Key point: for prototyping without sensitive data, Claude Code's built-in sandboxing is sufficient. For production with real user data, use Docker containers.
7. **Installed skills plugins** — installed an official coding/skills framework plugin (repo-scoped only)
 
### Understanding Skills
 
Dr. Nelson showed a previous project (grant writing) to explain skills:
 
**What is a skill?** A skill is basically a prompt that Claude can recognize it needs to use, stored as a markdown file in `.claude/commands/` (or `.claude/skills/`). It's like a mini sub-agent or a mini prompt for a specific step.
 
**Grant writing example skills:**
- A skill to simulate grant reviewers (with specific review criteria and questions)
- A skill to create revision plans from reviews
- A skill to execute revisions following the plan
 
**Project knowledge files:** Before making skills, populate the project with domain knowledge:
- Relevant text/documents (e.g., grant call for proposals)
- Prior work and examples (e.g., previously funded grants)
- Writing guidelines (e.g., "AI writing tropes to avoid")
- Relevant papers and research
 
**Running skills:** You tell Claude Code to use the skills and give it a prompt similar to what a user would say. It runs through the skills, generates outputs into files.
 
### Building the Mindful Consumption Agent
 
**The chosen project:** Idea #10 — an agent that helps people reduce wants for things they don't actually need, countering advertising and wasteful consumerism, encouraging human flourishing.
 
**Initial prompt to Claude Code:**
- Described the agent concept
- Asked it to create skills (not build a full application)
- Specified a "blend" personality: warm coach + Socratic guide + structured mentor
 
**Skills generated:**
1. `session-start` — Routes user intent to the appropriate skill
2. `want-examination` — Socratic questioning about purchases
3. `reframe` — Counters advertising/social pressure
4. `flourishing-prompt` — Self-care exercises
5. `gratitude-inventory` — Reflection on what you already have
 
**Key debugging moments:**
- Claude initially put skills in wrong directory (`skills/` instead of `.claude/commands/` or `.claude/skills/`)
- An installed plugin ("Superpowers") was interfering — its brainstorming skill was being called instead of the agent's own skills. Solution: disabled the plugin.
- Had to prompt Claude to fix the skill location and format
 
**First test run:**
- Role-played as "Maya" persona (impulse buyer, 28, UX designer)
- Input: "I've been feeling down and I think I deserve a whole new wardrobe"
- The agent used the `want-examination` skill correctly
- Asked good questions: "What shifts when you put on something new?"
- Explored the temporary nature of the confidence boost from shopping
- Transitioned to `flourishing-prompt` with "Three Good Things" exercise
 
**Observations during testing:**
- The agent sometimes went too deep into feelings ("getting too therapeutic")
- Needed faster redirection from examining the feeling to offering alternatives
- The "Three Good Things" exercise was actually good — "you can't really screw up asking someone to think about 3 good things"
 
### Collaborative Design Discussion (~11:17–11:26)
 
After the test run, Dr. Nelson, Cameron, and Brendon discussed:
 
**Key insight — Make it social:**
- The agent could be more social: "Hey, do you want to opt in so that when your friend is trying to buy something they don't need, it invites you into doing [a positive activity] with them?"
- Something really short/small, positive to do, good for you AND your friend
- Doing things with someone else overcomes inertia — "we won't do it because it feels cheesy, but doing it with someone else makes it more meaningful"
 
**Key insight — Simple interventions can work:**
- "Agents don't have to be complicated to work"
- Psychology theory might say there are 3 things helpful for distraction from impulse purchasing
- Just put A, B, and C in the prompts — simple, hard to screw up
 
**Key insight — Redirect, don't just examine:**
- Instead of only analyzing the want, redirect the impulse energy toward something positive
- Suggest concrete alternatives: call a friend, cook a meal, do something memorable
 
**Process insight — Collaborative prototyping is better:**
- "You need more than one person interacting together around AI and talking about it"
- "If I was doing this alone, I'd be like, okay, what's that do? It's like, why build interfaces that are lonely?"
- The most valuable ideas came from the human-to-human discussion, not from the AI
 
### Iteration and Version Control (~11:26–11:36)
 
- Fed the discussion transcript back into Claude Code to update the `flourishing-prompt` skill
- Created an experiment plan: "maya-1-plan-for-social-connection-suggesting"
- Used git branches for experiments: `experiment-one-social-recommendations`
- Committed frequently with descriptive messages
- Demonstrated moving files when Claude put them in wrong location — "supporting efficient easy correction"
 
### Key Prototyping Principles from the Demo:
 
1. **Prototyping is for learning, not building.** "The purpose of prototyping is not to build the thing, but to learn about what it is that you're building and why you're building it."
2. **Don't optimize too early.** Don't tweak individual prompt phrases — think about the bigger picture of agent behavior.
3. **Use simulated/fake data intentionally.** Even imagined interactions help refine design thinking.
4. **Commit frequently.** Every iteration should be a checkpoint.
5. **Multiple prototyping fidelities exist:**
   - Claude Code skills (fastest, most flexible, less accurate)
   - Actual agent framework with skills as tools/sub-agents (more accurate behavior)
   - Deployed on real platform with real users (highest fidelity)
6. **Feed collaborative discussions back into the agent.** Copy-paste Zoom transcript → Claude Code → updated skills.
7. **Watch what Claude actually does.** It may use wrong skills, wrong directories, or hallucinate behavior. Monitor and correct.
8. **The unhelpful examples matter as much as helpful ones.** Writing them defines boundaries.