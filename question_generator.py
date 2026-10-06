"""
question_generator.py
Generates a fresh interview question through the AI provider layer.
Falls back to question_selector when all providers are unavailable.
"""

import re
from ai_provider import request_ai
from question_selector import select_question


def generate_question(
    role: str,
    round_type: str,
    topic: str,
    difficulty: str,
    used_questions: list[str],
    weak_topics: list[str],
) -> dict:
    """
    Returns a question dict.  Uses AI if available, else the bank.
    """
    prompt = (
        f"Generate exactly ONE interview question for the following context.\n"
        f"Role: {role}\n"
        f"Interview round: {round_type}\n"
        f"Topic: {topic}\n"
        f"Difficulty: {difficulty}\n\n"
        f"Rules:\n"
        f"- Output ONLY the question text, nothing else.\n"
        f"- The question must be specific, technical and appropriate for an engineering campus interview.\n"
        f"- Do NOT include numbering, labels, or quotes.\n"
    )

    try:
        text, provider = request_ai(prompt)
        # Basic validation: reject if text is too short or looks like a prompt echo
        text = text.strip().strip('"').strip("'")
        if len(text) > 15 and "?" in text or len(text) > 40:
            return {
                "question": text,
                "role": role,
                "round": round_type,
                "topic": topic,
                "difficulty": difficulty,
                "importance": "Medium",
                "type": round_type,
                "source": f"AI ({provider})",
            }
    except Exception:
        pass  # fall through to bank

    # Fallback: question bank
    q = select_question(role, round_type, topic, difficulty, used_questions, weak_topics)
    if q:
        q = dict(q)
        q["source"] = "Bank (offline fallback)"
        return q

    return {
        "question": f"Explain a key concept related to {topic} for a {difficulty.lower()}-level {round_type} interview.",
        "role": role,
        "round": round_type,
        "topic": topic,
        "difficulty": difficulty,
        "importance": "Medium",
        "type": round_type,
        "source": "Hardcoded fallback",
    }
