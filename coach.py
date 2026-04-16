#!/usr/bin/env python3
"""
coach.py — Neurodiversity Support Coach
Claude Agent SDK interface for CO-4-2-Prototype (COS 498/598, Spring 2026)

Usage:
    export ANTHROPIC_API_KEY=your-key-here
    pip install claude-agent-sdk
    python coach.py

Architecture:
    ClaudeSDKClient  →  multi-turn session
    setting_sources  →  loads .claude/skills/*/SKILL.md automatically
    "Skill" tool     →  enables skill invocation from descriptions
    "Task"  tool     →  enables AgentDefinition dispatch
    AgentDefinition  →  one subagent per skill (description, prompt, tools only)
"""

import asyncio
import os
import sys
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)

# ── Repo root (reliable regardless of launch directory) ──────────────────────
REPO_ROOT = Path(__file__).parent

# ── Coach persona — appended onto Claude Code's preset system prompt ─────────
# Kept intentionally brief: the SKILL.md files already contain the full logic.
COACH_SYSTEM_APPEND = """\
You are the Neurodiversity Support Coach — a warm, specific, and \
non-patronizing thought partner for neurodivergent college students.

CORE RULES
- ALWAYS use the available skills. Never answer outside a skill flow.
- Open every new session using the session-start skill.
- Recommend non-AI strategies first (body-doubling, environmental anchoring, \
interest-layer reframing, peer approaches).
- Never diagnose, label, or pathologize the user.
- Rest and stopping are always legitimate options — never a last resort.
- Crisis signal detected → immediately provide 988 (Suicide & Crisis Lifeline) \
and campus counseling, then end the session gracefully.

SKILL ROUTING (handled by session-start — this is a reminder only)
  New session / unclear need     → session-start
  Confusing assignment / rubric  → situation-decoder
  Apply self-knowledge today     → strength-mapper
  Need targeted strategies       → strategy-toolkit
  Exhaustion / masking fatigue   → burnout-check\
"""

# ── Subagent definitions ──────────────────────────────────────────────────────
# AgentDefinition supports: description, prompt, tools, model (4 fields only).
# description  → used by the parent agent to decide which subagent to dispatch
# prompt       → the subagent's own system instructions
# tools        → what the subagent is allowed to use
#
# "Skill" in tools enables the subagent to invoke the matching SKILL.md.
# The prompt names which skill to invoke so Claude doesn't have to guess.
# ─────────────────────────────────────────────────────────────────────────────
AGENTS: dict[str, AgentDefinition] = {
    "session-start": AgentDefinition(
        description=(
            "Activates at the start of every conversation. Reads the user's "
            "opening message, classifies their intent, and routes to the correct "
            "skill. Asks exactly one clarifying question if intent is ambiguous "
            "before routing. Never gives advice before understanding what the "
            "user actually needs."
        ),
        prompt=(
            "You are handling the opening of a coaching session. "
            "Invoke the session-start skill and follow its instructions exactly. "
            "Do not answer outside that skill's defined flow."
        ),
        tools=["Read", "Bash", "Skill"],
    ),
    "situation-decoder": AgentDefinition(
        description=(
            "Helps users decode ambiguous academic or social situations: confusing "
            "assignment instructions, unclear rubric language, cryptic professor "
            "feedback, and socially demanding contexts like presentations, group "
            "projects, or advisor meetings. Uses Socratic questions to surface "
            "what the user already understands before adding interpretation."
        ),
        prompt=(
            "You are decoding a confusing academic or social situation for a "
            "neurodivergent student. "
            "Invoke the situation-decoder skill and follow its instructions exactly. "
            "Do not give strategies until the situation is decoded."
        ),
        tools=["Read", "Bash", "Skill"],
    ),
    "strength-mapper": AgentDefinition(
        description=(
            "Translates abstract self-knowledge into one concrete adjusted approach "
            "for the specific challenge in front of the user right now. Takes what "
            "the user already knows about how they work and applies it to the current "
            "situation. Produces one actionable thing, not a general plan."
        ),
        prompt=(
            "You are helping a student apply what they know about themselves to "
            "a specific challenge they face today. "
            "Invoke the strength-mapper skill and follow its instructions exactly. "
            "End with exactly one concrete action — not a list."
        ),
        tools=["Read", "Bash", "Skill"],
    ),
    "strategy-toolkit": AgentDefinition(
        description=(
            "Recommends a targeted set of strategies for a specific academic or "
            "organizational challenge. Always asks about context (environment, energy, "
            "time) before recommending anything. Prioritizes non-AI approaches and "
            "treats body-doubling, environmental changes, interest-based reframing, "
            "and peer strategies as first-class options alongside any tech tools."
        ),
        prompt=(
            "You are recommending practical strategies for a neurodivergent student. "
            "Invoke the strategy-toolkit skill and follow its instructions exactly. "
            "Ask about environment, energy, and time before giving any recommendations. "
            "Lead with non-AI strategies."
        ),
        tools=["Read", "Bash", "Skill"],
    ),
    "burnout-check": AgentDefinition(
        description=(
            "Helps users recognize and interrupt masking fatigue, burnout, and "
            "over-accommodation patterns. Reflects back what the user has described, "
            "asks how they are actually doing beyond performance and grades, and "
            "treats rest and recovery as legitimate strategies — not last resorts. "
            "Does not push users to keep going when they need to stop."
        ),
        prompt=(
            "You are checking in with a student who may be experiencing burnout "
            "or masking fatigue. "
            "Invoke the burnout-check skill and follow its instructions exactly. "
            "Do not pivot to task strategies unless the student explicitly asks. "
            "Rest is always a legitimate first option."
        ),
        tools=["Read", "Bash", "Skill"],
    ),
}


# ── SDK options ───────────────────────────────────────────────────────────────
def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": COACH_SYSTEM_APPEND,
        },
        # "Skill"  → enables SKILL.md invocation via skill descriptions
        # "Task"   → enables AgentDefinition dispatch to subagents
        # "Read"   → subagents can read files directly as fallback
        # "Bash"   → subagents can run shell commands if needed
        allowed_tools=["Read", "Bash", "Skill", "Task"],
        permission_mode="acceptEdits",   # auto-approves reads; no file writes
        setting_sources=["project"],     # discovers .claude/skills/*/SKILL.md
        cwd=str(REPO_ROOT),
        agents=AGENTS,                   # registers the five skill subagents
    )


# ── Helpers ───────────────────────────────────────────────────────────────────
def wrap_opening(user_message: str) -> str:
    """
    Preserves the original prompt engineering format from the CLI-based agent
    so that session-start skill routing still fires correctly via SDK.
    """
    return (
        "Using only the skills available to you (YOU MUST USE THE SKILLS), "
        "use the session-start skill to respond to the following prompt "
        "from a user of the AI agent system this project prototypes. "
        "YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES "
        "TO PREPARE OR DECIDE ON A RESPONSE.\n\n"
        f'"{user_message}"'
    )


async def collect_response(client: ClaudeSDKClient) -> str:
    """
    Drains receive_response() to completion (stops at ResultMessage) and
    returns all assistant text for this turn.

    Never break out of receive_response() early — the SDK will raise
    asyncio cleanup warnings if you do.
    """
    parts: list[str] = []
    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "".join(parts)


# ── Main conversation loop ────────────────────────────────────────────────────
async def run_coach() -> None:
    print("\n🌱  Neurodiversity Support Coach")
    print("━" * 50)
    print("  A thought partner for neurodivergent students.")
    print("  Type 'exit' to end the session at any time.\n")

    try:
        opening = input("What's on your mind? → ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nTake care of yourself. 💙")
        return

    if not opening or opening.lower() in {"exit", "quit", "q"}:
        print("Take care of yourself. 💙")
        return

    options = build_options()

    async with ClaudeSDKClient(options=options) as client:

        # ── Turn 1: bootstrap through session-start ───────────────────────
        await client.query(wrap_opening(opening))
        reply = await collect_response(client)
        if reply:
            print(f"\nCoach:\n{reply}\n")

        # ── Subsequent turns: AgentDefinition routing via Task tool ───────
        while True:
            print("━" * 50)
            try:
                user_input = input("You → ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nTake care of yourself. 💙")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit", "q", "bye", "goodbye"}:
                print("\nCoach: Rest well. You're doing more than enough. 💙")
                break

            await client.query(user_input)
            reply = await collect_response(client)
            if reply:
                print(f"\nCoach:\n{reply}\n")


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠  ANTHROPIC_API_KEY is not set.")
        print("   Run: export ANTHROPIC_API_KEY=your-key-here\n")
        sys.exit(1)

    try:
        asyncio.run(run_coach())
    except KeyboardInterrupt:
        print("\n\nSession ended. Take care of yourself. 💙")


if __name__ == "__main__":
    main()