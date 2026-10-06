"""
question_selector.py
Selects the best question from the question bank based on:
  role, round, topic, difficulty, importance, past practice, weak topics.
Falls back to generator when no suitable bank question is found.
"""

import random
from question_bank import get_all_questions


def select_question(
    role: str,
    round_type: str,
    topic: str,
    difficulty: str,
    used_questions: list[str],
    weak_topics: list[str],
) -> dict | None:
    """
    Return the best matching question dict, or None if no match found.
    Relaxes filters progressively: difficulty → topic → role.
    """
    pool = get_all_questions()

    def score(q: dict) -> int:
        s = 0
        # Exact matches
        if q["role"] == role:
            s += 10
        if q["round"].lower() == round_type.lower():
            s += 8
        if q["topic"] == topic:
            s += 6
        if q["difficulty"] == difficulty:
            s += 4
        # Not asked before
        if q["question"] not in used_questions:
            s += 5
        # High importance
        if q["importance"] == "High":
            s += 3
        elif q["importance"] == "Medium":
            s += 1
        # Weak topic boost
        if weak_topics and q["topic"] in weak_topics:
            s += 7
        return s

    # Filter: at minimum role OR topic must match
    candidates = [
        q for q in pool
        if (q["role"] == role or q["topic"] == topic)
        and q["question"] not in used_questions
    ]

    if not candidates:
        # Relax: any unused question
        candidates = [q for q in pool if q["question"] not in used_questions]

    if not candidates:
        # All questions used — reset
        candidates = pool[:]

    candidates.sort(key=score, reverse=True)
    # Add slight randomness among top 3 to avoid repeating identical order
    top = candidates[:3]
    return random.choice(top) if top else candidates[0]
