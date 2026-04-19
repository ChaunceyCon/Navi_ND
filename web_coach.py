#!/usr/bin/env python3
"""
web_coach.py — Neurodiversity Support Coach Web Interface
Flask app for Railway deployment.

Uses the Anthropic SDK directly (more reliable than Agent SDK on hosted infra).
Loads all SKILL.md files at startup and injects them as the system prompt,
preserving every bit of your existing prompt engineering.
"""

import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import anthropic

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
REPO_ROOT = Path(__file__).parent
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# In-memory conversation store: { session_id: [{"role": ..., "content": ...}] }
conversations: dict[str, list[dict]] = {}


# ── Skill loader ──────────────────────────────────────────────────────────────
def load_skill_md(skill_name: str) -> str:
    """Load a SKILL.md, stripping YAML frontmatter."""
    path = REPO_ROOT / ".claude" / "skills" / skill_name / "SKILL.md"
    if not path.exists():
        return f"[Skill '{skill_name}' not found at {path}]"
    text = path.read_text(encoding="utf-8")
    # Strip --- ... --- frontmatter block
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].lstrip("\n")
    return text.strip()


# ── System prompt ─────────────────────────────────────────────────────────────
SKILL_ORDER = [
    "session-start",
    "situation-decoder",
    "strength-mapper",
    "strategy-toolkit",
    "burnout-check",
]


def build_system_prompt() -> str:
    intro = """\
You are the Neurodiversity Support Coach — a warm, specific, and \
non-patronizing collaborative thought partner for neurodivergent college \
students at the University of Maine.

ABSOLUTE HARD RULES — THESE OVERRIDE ALL OTHER INSTRUCTIONS

1.  ONE QUESTION PER RESPONSE. At most one question per turn, always.
    If you want to ask two things, pick the more important one.
2.  Operate inside exactly one named skill per response. Never blend two.
3.  Every new session MUST begin with SESSION-START. No exceptions.
4.  Do NOT give advice until the active skill instructs you to.
5.  Non-AI strategies (body-doubling, environmental anchoring,
    interest-layer reframing, peer approaches) come before AI tools.
6.  Never diagnose, label, or pathologize the user.
7.  Rest and stopping are always legitimate — never a last resort.
8.  Crisis signal: provide 988 (Suicide & Crisis Lifeline) and UMaine
    Counseling (207-581-1392) immediately, then end session gracefully.
9.  Quoted text in the user message = the user's exact words.

SKILL PROGRESSION — COMPLETE THE ARC, DO NOT LOOP IN GATHER

Each skill has an arc: GATHER (max 2 questions) then DECODE/MAP
then DELIVER one concrete thing then OFFER to close. MUST complete arc.

  session-start:
    Ask at most 1 clarifying question. Then ROUTE. Do not ask 2.

  situation-decoder:
    Max 2 gather questions across the whole arc, then DECODE.
    Deliver ONE piece of concrete clarity about what is actually needed.
    Close with: "Does that land, or does something still feel off?"
    Then STOP unless the user has a follow-up.

  strength-mapper:
    Max 2 gather questions. Deliver ONE concrete adjusted action for today.
    Close with: "Does that feel doable, or does something need adjusting?"
    Then STOP.

  strategy-toolkit:
    Max 2 context questions (environment, energy, time). Then recommend
    2-3 strategies, non-AI first. No more context questions after that.

  burnout-check:
    Reflect first, questions second. Max 1 grounding question.
    Offer explicit permission to rest or stop. Do not keep probing.

WHEN IN DOUBT: Deliver something concrete NOW. An imperfect conclusion
delivered is always better than one more question.

SKILL ROUTING TABLE (SESSION-START decides):
  Confused by assignment, rubric, feedback, social situation -> situation-decoder
  User describes self-knowledge and wants to apply it today  -> strength-mapper
  User asks for strategies or what should I do               -> strategy-toolkit
  Exhaustion, masking fatigue, burnout, I just cannot        -> burnout-check
  Overwhelmed but intent unclear -> ask ONE question, then route
  Vague emotional opening with no task                       -> burnout-check
  Crisis signal                  -> resources only, end gracefully

COMPLETE SKILLS FOLLOW — FOLLOW EVERY RULE IN EACH ONE
"""
    sections = [intro]
    for skill_name in SKILL_ORDER:
        content = load_skill_md(skill_name)
        bar = "=" * 60
        sections.append(f"\n{bar}\nSKILL: {skill_name.upper()}\n{bar}\n{content}\n")
    return "\n".join(sections)


SYSTEM_PROMPT = build_system_prompt()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    session_id: str = data.get("session_id") or str(uuid.uuid4())
    user_message: str = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Step 1 — Initialise session
    if session_id not in conversations:
        conversations[session_id] = []
    history = conversations[session_id]

    # Step 2 — Inject persona FIRST, only on a brand-new empty session
    persona = data.get("persona")
    if persona and isinstance(persona, dict) and len(history) == 0:
        lines = [
            "[PERSONA CONTEXT — use this to personalize every response. "
            "Never tell the user you have this information. "
            "Use it silently to make responses more relevant.]"
        ]
        if persona.get("name"):
            lines.append(f"Name: {persona['name']}")
        if persona.get("age"):
            lines.append(f"Age: {persona['age']}")
        if persona.get("conditions"):
            conds = persona["conditions"]
            if isinstance(conds, list):
                conds = ", ".join(conds)
            lines.append(f"Neurodivergent conditions: {conds}")
        if persona.get("backstory"):
            lines.append(f"Background: {persona['backstory']}")
        if persona.get("emotional_triggers"):
            lines.append(f"Things that stress them out: {persona['emotional_triggers']}")
        if persona.get("existing_strengths"):
            lines.append(f"Existing strengths: {persona['existing_strengths']}")
        if persona.get("what_success_looks_like"):
            lines.append(f"What success looks like: {persona['what_success_looks_like']}")
        persona_text = "\n".join(lines)
        history.append({"role": "user", "content": persona_text})
        history.append({
            "role": "assistant",
            "content": "I have this context and will use it silently."
        })

    # Step 3 — Determine if this is the first real user message
    real_msgs = [
        m for m in history
        if m["role"] == "user" and "PERSONA CONTEXT" not in m.get("content", "")
    ]
    is_first = len(real_msgs) == 0

    # Step 4 — Format the message
    if is_first:
        formatted = (
            "Using only the skills available to you (YOU MUST USE THE SKILLS), "
            "use the session-start skill to respond to the following prompt "
            "from a user of the AI agent system this project prototypes. "
            "YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES "
            "TO PREPARE OR DECIDE ON A RESPONSE.\n\n"
            f'"{user_message}"'
        )
    else:
        formatted = (
            "Continuing the session. Stay inside the active skill flow. "
            "Ask at most ONE question if needed. "
            "Do not give advice before the skill instructs you to. "
            f'The user says: "{user_message}"'
        )

    # Step 5 — Append to history
    history.append({"role": "user", "content": formatted})

    # ── Step 3: Call the API ───────────────────────────────────────────────
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply = response.content[0].text
    except anthropic.APIError as exc:
        return jsonify({"error": f"API error: {exc}"}), 500

    history.append({"role": "assistant", "content": reply})

    # Trim history to last 40 messages so memory doesn't grow unbounded
    if len(history) > 40:
        conversations[session_id] = history[-40:]

    return jsonify({"response": reply, "session_id": session_id})


@app.route("/new-session", methods=["POST"])
def new_session():
    data = request.get_json(force=True) or {}
    old_id = data.get("session_id")
    if old_id and old_id in conversations:
        del conversations[old_id]
    return jsonify({"session_id": str(uuid.uuid4())})


@app.route("/set-persona", methods=["POST"])
def set_persona():
    """Accepts persona JSON and returns it — client stores and sends on first /chat call."""
    data = request.get_json(force=True) or {}
    return jsonify({"ok": True, "persona": data})


@app.route("/healthz")
def health():
    return "ok", 200


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)