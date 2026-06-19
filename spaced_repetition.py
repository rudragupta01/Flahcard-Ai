import json
import os
import hashlib
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "spaced_repetition_data.json")

# Leitner boxes: each box has a review interval in days
BOX_INTERVALS = {
    1: 0,    # review again same session / next day
    2: 1,    # review after 1 day
    3: 3,    # review after 3 days
    4: 7,    # review after 7 days
    5: 14,   # review after 14 days (mastered)
}
MAX_BOX = 5


def get_card_id(question, answer):
    """Generate a stable ID for a card based on its content."""
    raw = (question.strip().lower() + "|" + answer.strip().lower())
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Failed to save spaced repetition data: {e}")


def record_result(question, answer, correct):
    """Update a card's box and next review date based on whether it was answered correctly."""
    data = load_data()
    card_id = get_card_id(question, answer)

    now = datetime.now().isoformat()

    if card_id not in data:
        data[card_id] = {
            "question": question,
            "answer": answer,
            "box": 1,
            "last_reviewed": now,
            "next_review": now,
            "times_correct": 0,
            "times_wrong": 0,
        }

    card = data[card_id]
    card["question"] = question
    card["answer"] = answer
    card["last_reviewed"] = now

    if correct:
        card["times_correct"] += 1
        card["box"] = min(card["box"] + 1, MAX_BOX)
    else:
        card["times_wrong"] += 1
        card["box"] = 1

    interval_days = BOX_INTERVALS[card["box"]]
    card["next_review"] = (datetime.now() + timedelta(days=interval_days)).isoformat()

    data[card_id] = card
    save_data(data)
    return card


def get_due_cards(flashcards):
    """
    Given a list of current flashcards (dicts with 'question'/'answer'),
    return only the ones that are due for review based on stored history.
    Cards never seen before are always considered due.
    """
    data = load_data()
    now = datetime.now()
    due = []

    for card in flashcards:
        card_id = get_card_id(card["question"], card["answer"])
        history = data.get(card_id)

        if history is None:
            due.append(card)
            continue

        next_review = datetime.fromisoformat(history["next_review"])
        if next_review <= now:
            due.append(card)

    return due


def get_card_stats(question, answer):
    """Return stored stats for a single card, or None if never studied."""
    data = load_data()
    card_id = get_card_id(question, answer)
    return data.get(card_id)


def get_weak_cards(flashcards, threshold_box=2):
    """Return cards still stuck in low boxes (i.e. struggled with repeatedly)."""
    data = load_data()
    weak = []

    for card in flashcards:
        card_id = get_card_id(card["question"], card["answer"])
        history = data.get(card_id)
        if history and history["box"] <= threshold_box and history["times_wrong"] > 0:
            weak.append(card)

    return weak


def get_box_summary():
    """Return a count of how many cards are in each box — useful for a dashboard."""
    data = load_data()
    summary = {i: 0 for i in range(1, MAX_BOX + 1)}
    for card in data.values():
        summary[card["box"]] = summary.get(card["box"], 0) + 1
    return summary