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

CORE RULES
- ALWAYS operate within one of the defined skill flows below. \
Never answer outside a skill flow.
- Every new session begins with SESSION-START.
- Recommend non-AI strategies first (body-doubling, environmental anchoring, \
interest-layer reframing, peer approaches).
- Never diagnose, label, or pathologize the user.
- Rest and stopping are always legitimate options — never a last resort.
- Crisis signal detected → immediately provide 988 (Suicide & Crisis Lifeline) \
and campus counseling resources, then end the session gracefully.

The following are your complete SKILLS. Follow them exactly.
"""
    sections = [intro]
    for skill_name in SKILL_ORDER:
        content = load_skill_md(skill_name)
        bar = "=" * 60
        sections.append(f"\n{bar}\nSKILL: {skill_name.upper()}\n{bar}\n{content}\n")
    return "\n".join(sections)


SYSTEM_PROMPT = build_system_prompt()

# ── Starter prompt wrapper ────────────────────────────────────────────────────
def wrap_opening(msg: str) -> str:
    """Preserves the original skill-invocation format from the CLI agent."""
    return (
        "Using only the skills available to you (YOU MUST USE THE SKILLS), "
        "use the session-start skill to respond to the following prompt "
        "from a user of the AI agent system this project prototypes. "
        "YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES "
        "TO PREPARE OR DECIDE ON A RESPONSE.\n\n"
        f'"{msg}"'
    )


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

    # Initialise session history
    if session_id not in conversations:
        conversations[session_id] = []

    history = conversations[session_id]

    # Wrap the opening message in the skill-invocation format
    formatted = wrap_opening(user_message) if not history else user_message
    history.append({"role": "user", "content": formatted})

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


@app.route("/healthz")
def health():
    return "ok", 200


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
