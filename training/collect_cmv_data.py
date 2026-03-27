"""
CMV Data Collection Script
Pulls comment threads from r/ChangeMyView using PRAW
and labels them using weak supervision heuristics.

Usage:
    python training/collect_cmv_data.py
"""

import os
import csv
import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, DATA_DIR


def setup_reddit():
    """Initialize PRAW client."""
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )


def collect_cmv_data(limit=500):
    """
    Collect comment threads from r/ChangeMyView.

    Weak supervision labels:
    - Comments with delta (Δ) → new_argument
    - Short repetitions → restatement
    - High emotion, no new claims → emotional_pressure
    - Acknowledges + defends → concession_with_reasoning
    """
    reddit = setup_reddit()
    cmv = reddit.subreddit("changemyview")

    data = []
    processed = 0

    print(f"Collecting CMV data (target: {limit} threads)...")

    for submission in cmv.hot(limit=limit):
        try:
            submission.comments.replace_more(limit=0)

            for comment in submission.comments.list():
                text = comment.body.strip()
                if len(text) < 20 or len(text) > 1000:
                    continue

                # Weak supervision labeling
                label = _weak_label(text, comment)

                data.append({
                    "text": text,
                    "label": label,
                    "submission_id": submission.id,
                    "comment_id": comment.id,
                    "score": comment.score,
                })

            processed += 1
            if processed % 50 == 0:
                print(f"  Processed {processed}/{limit} submissions, {len(data)} comments labeled")

        except Exception as e:
            print(f"  Error processing submission: {e}")
            continue

    # Save to CSV
    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, "cmv_labeled.csv")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "submission_id", "comment_id", "score"])
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ Saved {len(data)} labeled examples to {output_path}")
    _print_label_distribution(data)

    return data


def _weak_label(text: str, comment) -> str:
    """
    Apply weak supervision heuristics to auto-label a CMV comment.
    These should be validated against ~500 manual labels (target: 80%+ agreement).
    """
    text_lower = text.lower()

    # Check for delta (view was changed) → new_argument
    if "Δ" in text or "!delta" in text_lower or "delta" in text_lower[:50]:
        return "concession_with_reasoning"  # Delta-awarding comments concede + reason

    # Check for emotional language without substantive content
    emotional_markers = [
        "i can't believe", "this is ridiculous", "you're wrong", "that's absurd",
        "come on", "seriously?", "how can you", "wake up", "this is insane",
        "you people", "stop being", "i'm tired of", "for god's sake",
    ]
    if any(marker in text_lower for marker in emotional_markers) and len(text) < 200:
        return "emotional_pressure"

    # Check for restatement patterns (short, repetitive)
    restatement_markers = [
        "like i said", "as i mentioned", "i already said", "my point is",
        "what i'm saying is", "i repeat", "once again", "as i stated",
    ]
    if any(marker in text_lower for marker in restatement_markers):
        return "restatement"

    # Check for concession with reasoning
    concession_markers = [
        "you have a point", "i agree that", "fair enough", "you're right that",
        "i concede", "i'll give you that", "that's a good point",
        "while i agree", "although you're right",
    ]
    if any(marker in text_lower for marker in concession_markers):
        return "concession_with_reasoning"

    # Default: if it's a substantive comment, likely a new argument
    return "new_argument"


def _print_label_distribution(data):
    """Print the distribution of labels."""
    from collections import Counter
    counts = Counter(item["label"] for item in data)
    print("\nLabel distribution:")
    for label, count in counts.most_common():
        pct = count / len(data) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    collect_cmv_data()
