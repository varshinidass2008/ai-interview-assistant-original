"""
priority_engine.py
Computes topic priorities from interview history.

Priority(t) = w1*(1 - Performance(t))
            + w2*Importance(t)
            + w3*Mistakes(t)
            + w4*Recency(t)
            + w5*WeakHistory(t)

Returns ranked list of topics for the dashboard and question selector.
"""

import json
import os
from datetime import date, datetime
from collections import defaultdict
from interview_history import load_history

# Configurable weights
W1 = 0.35  # poor performance
W2 = 0.20  # importance
W3 = 0.20  # repeated mistakes
W4 = 0.15  # recency (time since last practice)
W5 = 0.10  # weak-topic history count

IMPORTANCE_MAP = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
SCORE_MAP = {
    "Excellent": 1.0,
    "Good": 0.75,
    "Average": 0.5,
    "Needs Improvement": 0.2,
    "Not Attempted": 0.0,
    "Evaluated": 0.5,
}


def compute_priorities(username: str, urgency_days: int = 20) -> list[dict]:
    """
    Returns list of dicts sorted by priority score (highest first).
    Each dict: {topic, priority_score, avg_performance, practice_count, flagged_weak}
    """
    history = load_history(username)
    if not history:
        return []

    topic_data = defaultdict(lambda: {
        "scores": [],
        "dates": [],
        "importance_values": [],
        "weak_flags": 0,
    })

    for record in history:
        t = record.get("topic", "Unknown")
        score_label = record.get("score_label", "Average")
        score_val = SCORE_MAP.get(score_label, 0.5)
        imp = record.get("importance", "Medium")
        imp_val = IMPORTANCE_MAP.get(imp, 0.6)
        rec_date = record.get("date", str(date.today()))
        is_weak = score_val <= 0.5

        topic_data[t]["scores"].append(score_val)
        topic_data[t]["dates"].append(rec_date)
        topic_data[t]["importance_values"].append(imp_val)
        if is_weak:
            topic_data[t]["weak_flags"] += 1

    results = []
    today = date.today()

    for topic, td in topic_data.items():
        scores = td["scores"]
        avg_perf = sum(scores) / len(scores)
        importance = sum(td["importance_values"]) / len(td["importance_values"])
        practice_count = len(scores)
        weak_flags = td["weak_flags"]

        # Recency: days since last practice (capped at 30)
        last_date = max(td["dates"])
        try:
            days_ago = (today - date.fromisoformat(last_date)).days
        except Exception:
            days_ago = 10
        recency = min(days_ago, 30) / 30  # 0 = practiced today, 1 = 30+ days ago

        # Repeated mistakes: fraction of attempts that were poor
        mistakes = sum(1 for s in scores if s <= 0.5) / max(practice_count, 1)

        # Weak history: normalized (cap at 10)
        weak_history = min(weak_flags, 10) / 10

        # Urgency multiplier
        if urgency_days <= 1:
            urgency_mult = 1.5
        elif urgency_days <= 3:
            urgency_mult = 1.25
        else:
            urgency_mult = 1.0

        priority_score = urgency_mult * (
            W1 * (1 - avg_perf)
            + W2 * importance
            + W3 * mistakes
            + W4 * recency
            + W5 * weak_history
        )

        results.append({
            "topic": topic,
            "priority_score": round(priority_score, 3),
            "avg_performance": round(avg_perf, 2),
            "practice_count": practice_count,
            "flagged_weak": weak_flags,
            "last_practiced": last_date,
        })

    results.sort(key=lambda x: x["priority_score"], reverse=True)
    return results


def get_weak_topics(username: str, top_n: int = 3) -> list[str]:
    priorities = compute_priorities(username)
    return [p["topic"] for p in priorities[:top_n] if p["avg_performance"] < 0.65]
