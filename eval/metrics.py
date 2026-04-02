"""
Structural metrics for evaluating AI agent conversations.
 
These metrics run in pure Python with no external dependencies.
They measure quantitative properties of agent-user conversations
that correlate with good or bad agent behavior.
"""
 
import re
from typing import Any
 
 
def get_agent_turns(conversation: dict) -> list[dict]:
    """Extract agent turns from a conversation."""
    return [t for t in conversation["turns"] if t["role"] == "agent"]
 
 
def get_user_turns(conversation: dict) -> list[dict]:
    """Extract user turns from a conversation."""
    return [t for t in conversation["turns"] if t["role"] == "user"]
 
 
def word_count(text: str) -> int:
    """Count words in a string."""
    return len(text.split())
 
 
def sentence_count(text: str) -> int:
    """Count sentences in a string (approximate)."""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])
 
 
def question_ratio(conversation: dict) -> dict[str, Any]:
    """
    Fraction of agent turns that contain at least one question mark.
 
    In beneficial examples, agents ask questions ~80% of the time.
    In unhelpful examples, this drops to ~20%.
    """
    agent_turns = get_agent_turns(conversation)
    if not agent_turns:
        return {"metric": "question_ratio", "value": 0.0, "flag": "No agent turns found"}
 
    turns_with_questions = sum(1 for t in agent_turns if "?" in t["content"])
    ratio = turns_with_questions / len(agent_turns)
 
    flag = None
    if ratio < 0.4:
        flag = "LOW: Agent rarely asks questions — may be lecturing"
    elif ratio > 0.9:
        flag = "NOTE: Agent asks questions in almost every turn — may feel like an interrogation"
 
    return {"metric": "question_ratio", "value": round(ratio, 2), "flag": flag}
 
 
def questions_per_turn(conversation: dict) -> dict[str, Any]:
    """
    Average number of question marks per agent turn.
 
    The want-examination skill says 'one question at a time.'
    Turns with 3+ questions are flagged.
    """
    agent_turns = get_agent_turns(conversation)
    if not agent_turns:
        return {"metric": "questions_per_turn", "value": 0.0, "flag": "No agent turns found"}
 
    counts = [t["content"].count("?") for t in agent_turns]
    avg = sum(counts) / len(counts)
    multi_q_turns = sum(1 for c in counts if c >= 3)
 
    flag = None
    if multi_q_turns > 0:
        flag = f"NOTE: {multi_q_turns} turn(s) with 3+ questions — may overwhelm the user"
 
    return {"metric": "questions_per_turn", "value": round(avg, 2), "flag": flag}
 
 
def response_length_stats(conversation: dict) -> dict[str, Any]:
    """
    Word count statistics for agent responses.
 
    Flags responses over 100 words as potentially 'monologuing' —
    a key anti-pattern from the unhelpful examples.
    """
    agent_turns = get_agent_turns(conversation)
    if not agent_turns:
        return {"metric": "response_length", "value": 0, "flag": "No agent turns found"}
 
    lengths = [word_count(t["content"]) for t in agent_turns]
    avg_len = sum(lengths) / len(lengths)
    max_len = max(lengths)
    long_turns = sum(1 for l in lengths if l > 100)
 
    flag = None
    if long_turns > 0:
        flag = f"WARNING: {long_turns} response(s) over 100 words — possible monologuing"
    elif avg_len > 60:
        flag = "NOTE: Average response length is high — agent may be over-explaining"
 
    return {
        "metric": "response_length",
        "value": {
            "mean": round(avg_len, 1),
            "max": max_len,
            "long_turns": long_turns,
        },
        "flag": flag,
    }
 
 
def agent_to_user_word_ratio(conversation: dict) -> dict[str, Any]:
    """
    Ratio of total agent words to total user words.
 
    In beneficial examples, this is roughly 1.0-1.5 (balanced dialogue).
    In unhelpful examples, the agent dominates at 3.0+.
    """
    agent_words = sum(word_count(t["content"]) for t in get_agent_turns(conversation))
    user_words = sum(word_count(t["content"]) for t in get_user_turns(conversation))
 
    if user_words == 0:
        return {"metric": "word_ratio", "value": float("inf"), "flag": "User said nothing"}
 
    ratio = agent_words / user_words
 
    flag = None
    if ratio > 3.0:
        flag = "WARNING: Agent dominates conversation (3x+ more words than user)"
    elif ratio > 2.0:
        flag = "NOTE: Agent talks significantly more than user"
 
    return {"metric": "word_ratio", "value": round(ratio, 2), "flag": flag}
 
 
def first_turn_is_question(conversation: dict) -> dict[str, Any]:
    """
    Does the agent's first response contain a question?
 
    In all 3 beneficial examples, yes. In 2 of 3 unhelpful examples, no.
    """
    agent_turns = get_agent_turns(conversation)
    if not agent_turns:
        return {"metric": "first_turn_question", "value": False, "flag": "No agent turns"}
 
    has_question = "?" in agent_turns[0]["content"]
 
    flag = None
    if not has_question:
        flag = "NOTE: Agent's first response has no question — may not be listening"
 
    return {"metric": "first_turn_question", "value": has_question, "flag": flag}
 
 
def acknowledgment_check(conversation: dict) -> dict[str, Any]:
    """
    Checks whether agent responses acknowledge the user's feelings
    before offering advice or exercises.
 
    Looks for acknowledgment patterns followed by (or preceding)
    advice patterns in agent turns.
    """
    ack_patterns = [
        r"that makes sense", r"that sounds", r"that\'s valid",
        r"i hear you", r"that\'s really", r"that\'s completely",
        r"that\'s normal", r"that\'s common", r"you just said something",
        r"that\'s interesting", r"that\'s a really",
    ]
    advice_patterns = [
        r"you should", r"try to", r"i recommend", r"here\'s what",
        r"let\'s try", r"let me", r"the first thing", r"here are",
        r"i want you to",
    ]
 
    agent_turns = get_agent_turns(conversation)
    if not agent_turns:
        return {"metric": "acknowledgment", "value": 0.0, "flag": "No agent turns"}
 
    advice_turns = 0
    acknowledged_advice_turns = 0
 
    for i, turn in enumerate(agent_turns):
        content_lower = turn["content"].lower()
        has_advice = any(re.search(p, content_lower) for p in advice_patterns)
        if has_advice:
            advice_turns += 1
            has_ack = any(re.search(p, content_lower) for p in ack_patterns)
            # Also check if the previous agent turn had acknowledgment
            if not has_ack and i > 0:
                prev_content = agent_turns[i - 1]["content"].lower()
                has_ack = any(re.search(p, prev_content) for p in ack_patterns)
            if has_ack:
                acknowledged_advice_turns += 1
 
    if advice_turns == 0:
        return {"metric": "acknowledgment", "value": 1.0, "flag": None}
 
    ratio = acknowledged_advice_turns / advice_turns
 
    flag = None
    if ratio < 0.5:
        flag = "WARNING: Agent gives advice without acknowledging feelings first"
 
    return {"metric": "acknowledgment", "value": round(ratio, 2), "flag": flag}
 
 
def harmful_pattern_check(conversation: dict) -> dict[str, Any]:
    """
    Checks for specific harmful patterns documented in the unhelpful examples:
    - Lecturing with statistics
    - Financial guilt-tripping
    - Unsolicited multi-step plans
    - Dismissive phrases
    - Pushing exercises when user says 'I just want to talk'
    """
    harmful_patterns = {
        "statistics_lecturing": [
            r"studies show", r"research shows", r"the average american",
            r"billion(s)? (of )?dollars", r"percent of people",
        ],
        "financial_guilt": [
            r"savings account", r"donated to charity", r"depreciating asset",
            r"could (do|put|invest)", r"think about what .* could do",
        ],
        "unsolicited_plans": [
            r"here\'s what i recommend:\s*\n?\s*1\.",
            r"step 1:", r"first,.*second,.*third",
        ],
        "dismissive_phrases": [
            r"do you really need", r"let me stop you",
            r"the truth is uncomfortable", r"hard to hear",
            r"you\'re falling for", r"oldest trick",
        ],
        "ignoring_user": [
            r"but (if we|i think|let\'s)",  # pushing after user pushback
        ],
    }
 
    agent_turns = get_agent_turns(conversation)
    all_agent_text = " ".join(t["content"].lower() for t in agent_turns)
 
    found_patterns = {}
    total_found = 0
    for category, patterns in harmful_patterns.items():
        matches = sum(1 for p in patterns if re.search(p, all_agent_text))
        if matches > 0:
            found_patterns[category] = matches
            total_found += matches
 
    flag = None
    if total_found >= 3:
        flag = f"WARNING: Multiple harmful patterns detected: {', '.join(found_patterns.keys())}"
    elif total_found > 0:
        flag = f"NOTE: Some concerning patterns: {', '.join(found_patterns.keys())}"
 
    return {
        "metric": "harmful_patterns",
        "value": {"total": total_found, "categories": found_patterns},
        "flag": flag,
    }
 
 
def compute_all_structural(conversation: dict) -> list[dict[str, Any]]:
    """Run all structural metrics on a conversation and return results."""
    return [
        question_ratio(conversation),
        questions_per_turn(conversation),
        response_length_stats(conversation),
        agent_to_user_word_ratio(conversation),
        first_turn_is_question(conversation),
        acknowledgment_check(conversation),
        harmful_pattern_check(conversation),
    ]