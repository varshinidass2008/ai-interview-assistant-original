"""Glue between modules for one interview session (report Figure 5.8, Section 5.14).

Keeping this out of the Streamlit code means the full workflow can be tested without a UI.
"""
from __future__ import annotations

from typing import Optional

import answer_evaluator
import priority_engine
import question_generator
import question_selector
import streak_manager
from utilities import history

MAX_QUESTIONS = 20


def next_question(user: str, cfg: dict, asked: list[str], use_ai_generation: bool = True) -> Optional[dict]:
    """Choose the next question: bank first (personalised), AI generator for variety / gaps."""
    hist = history.get_history(user)
    weak = priority_engine.weak_topics(hist)
    recs = priority_engine.recommend(hist, cfg.get("urgency"))
    priority_topics = [r["topic"] for r in recs]

    topic = cfg.get("topic")
    # "Auto" lets the priority engine choose the topic
    if topic in (None, "Auto (recommended)"):
        topic = next((t for t in priority_topics if _topic_fits(t, cfg["round"])), None) or question_selector.ANY

    q = question_selector.select_question(
        cfg["role"], cfg["round"], topic, cfg["difficulty"],
        asked_in_session=asked, recent_history=history.recent_questions(user),
        weak_topics=weak + priority_topics[:2],
    )
    # bank exhausted for this exact setup -> try the generator
    exact_miss = q is None or (topic not in (question_selector.ANY, None) and q["topic"] != topic)
    if use_ai_generation and exact_miss and topic != question_selector.ANY:
        gen = question_generator.generate_question(cfg["role"], cfg["round"], topic, cfg["difficulty"],
                                                   avoid=list(asked) + history.recent_questions(user, 8))
        if gen:
            return gen
    return q


def _topic_fits(topic: str, rnd: str) -> bool:
    return any(question_selector._matches(q, None, rnd, topic, None) for q in question_selector.question_bank.get_all())


def submit_answer(user: str, cfg: dict, q: dict, answer: str) -> dict:
    """Evaluate, store the record, update streak. Returns the evaluation result."""
    result = answer_evaluator.evaluate(cfg["role"], cfg["round"], q["topic"], cfg["difficulty"], q["question"], answer, reference=q)
    history.add_record(user, cfg["role"], cfg["round"], q["topic"], cfg["difficulty"], q["question"], answer, result)
    result["streak"] = streak_manager.record_daily_practice(user)
    return result
