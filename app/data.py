# data.py

import json
import os

SESSION_FILE = "last_session.json"
STATS_FILE = "stats.json"

def make_json_serializable(obj):
    """Rekurzivně převádí všechny sety na listy v dictu/listu."""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj

def load_questions_from_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        raw = json.load(f)
        for q in raw:
            q["answer"] = set(q["answer"])
        return raw

def load_stats(filename=STATS_FILE):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats, filename=STATS_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

def save_session(data, filename=SESSION_FILE):
    data = make_json_serializable(data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_session(filename=SESSION_FILE):
    if not os.path.exists(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def clear_session(filename=SESSION_FILE):
    if os.path.exists(filename):
        os.remove(filename)

def session_exists(filename=SESSION_FILE):
    """Vrací True pokud existuje session soubor."""
    return os.path.exists(filename)

def stats_exists(filename=STATS_FILE):
    """Vrací True pokud existuje stats soubor."""
    return os.path.exists(filename)
