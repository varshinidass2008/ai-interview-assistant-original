"""
interview_history.py
Stores and retrieves interview attempt records.
Each record: date, role, round, topic, difficulty, question,
             answer, score_label, evaluation, feedback fields, importance.
"""

import json
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def _history_path(username: str) -> str:
    return os.path.join(DATA_DIR, f"history_{username}.json")


def load_history(username: str) -> list[dict]:
    path = _history_path(username)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def save_attempt(username: str, record: dict):
    """Append a single attempt record to the user's history file."""
    history = load_history(username)
    record.setdefault("date", str(date.today()))
    history.append(record)
    with open(_history_path(username), "w") as f:
        json.dump(history, f, indent=2)


def get_recent(username: str, n: int = 5) -> list[dict]:
    history = load_history(username)
    return history[-n:][::-1]


def get_completed_count(username: str) -> int:
    return len(load_history(username))
