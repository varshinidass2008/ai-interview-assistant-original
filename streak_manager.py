"""
streak_manager.py
Maintains the daily practice streak.
  record_daily_practice(username)  →  updates streak
  get_streak_info(username)        →  returns dict with streak, dates, etc.
"""

import json
import os
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def _streak_path(username: str) -> str:
    return os.path.join(DATA_DIR, f"streak_{username}.json")


def _load(username: str) -> dict:
    path = _streak_path(username)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"streak": 0, "last_practice": None, "practice_dates": []}


def _save(username: str, data: dict):
    with open(_streak_path(username), "w") as f:
        json.dump(data, f, indent=2)


def record_daily_practice(username: str) -> dict:
    """
    Call once per completed practice session.
    Updates streak according to:
      - same day       → streak unchanged
      - previous day   → streak + 1
      - gap > 1 day    → streak = 1
    Returns updated streak info dict.
    """
    data = _load(username)
    today = str(date.today())
    last = data.get("last_practice")

    if last == today:
        pass  # already recorded today
    elif last is None:
        data["streak"] = 1
        data["last_practice"] = today
        dates = data.get("practice_dates", [])
        if today not in dates:
            dates.append(today)
        data["practice_dates"] = dates
    else:
        last_date = date.fromisoformat(last)
        today_date = date.fromisoformat(today)
        diff = (today_date - last_date).days
        if diff == 1:
            data["streak"] = data.get("streak", 0) + 1
        else:
            data["streak"] = 1
        data["last_practice"] = today
        dates = data.get("practice_dates", [])
        if today not in dates:
            dates.append(today)
        data["practice_dates"] = dates

    _save(username, data)
    return data


def get_streak_info(username: str) -> dict:
    return _load(username)
