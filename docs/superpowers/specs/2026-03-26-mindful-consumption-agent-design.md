# Mindful Consumption Agent — Design Spec

## Purpose

An AI agent that helps people reduce unnecessary wants driven by advertising and consumerism. Encourages human flourishing through self-care, empathy, gratitude, and reflective questioning. Runs as a Claude Code CLI simulation using Claude Skills.

## Architecture

### Skills (5 total, in `.claude/skills/`)

| Skill | Trigger | Approach | Tone |
|-------|---------|----------|------|
| `session-start` | Every conversation start | Reads persona context, classifies user intent, routes to appropriate skill | Warm, welcoming |
| `want-examination` | User expresses desire to buy/acquire | Socratic questioning: what need does this fulfill? what happened last time? what do you already have? | Socratic guide |
| `reframe` | User mentions ads, social comparison, "everyone has X" | Names the persuasion technique, reframes want as underlying human need, suggests non-purchase alternatives | Structured mentor |
| `flourishing-prompt` | User is stressed, low, or asks for self-care | Offers scaled exercises: gratitude micro-journal, body scan, "three good things," empathy prompts | Structured mentor |
| `gratitude-inventory` | General check-in, or session closer | Guides listing of satisfying things user already has, surfaces patterns | Warm coach |

### Workflow

```
User opens session
       |
       v
  session-start (classifies intent)
       |
       +---> "I want to buy X" ---> want-examination
       |                                  |
       |                           mentions ads? ---> reframe
       |
       +---> "I feel stressed" ---> flourishing-prompt
       |
       +---> general check-in ---> gratitude-inventory
       |
       v
  Any path can close with gratitude-inventory
```

**Rules:**
- `session-start` always fires first
- Skills can chain (want-examination -> reframe is common)
- `gratitude-inventory` is a natural session closer
- Agent can stay in one skill for a full session
- Tone adapts: warm by default, Socratic during want-examination, structured during flourishing-prompt

### Personas (4, in `data/personas/`)

1. **Maya, 28, UX Designer** — Impulse buyer, shops when stressed, 30+ unopened packages
2. **David, 45, Sales Manager** — Status buyer, premium brands = success identity
3. **Priya, 34, Freelance Writer** — Scarcity-anxiety buyer, hoards deals from financial instability background
4. **Jordan, 22, College Student** — Social-media-influenced, buys what TikTok recommends

### Interaction Examples (in `data/interactions/`)

**Beneficial (3):** Agent successfully helps user reflect, reframe, or find non-purchase alternatives
**Unhelpful (3):** Agent is preachy, dismissive, gives unsolicited lectures, or shames the user

## File Structure

```
.claude/skills/
  session-start.md
  want-examination.md
  reframe.md
  flourishing-prompt.md
  gratitude-inventory.md
data/personas/
  maya.json
  david.json
  priya.json
  jordan.json
data/interactions/
  beneficial-01-maya-impulse.md
  beneficial-02-david-status.md
  beneficial-03-jordan-tiktok.md
  unhelpful-01-preachy-lecture.md
  unhelpful-02-dismissive-shame.md
  unhelpful-03-unsolicited-advice.md
```
