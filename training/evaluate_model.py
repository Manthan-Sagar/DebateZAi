"""
Model Evaluation Script — evaluates the trained stance classifier.
Prints accuracy, per-class F1, and confusion matrix.

Usage:
    python training/evaluate_model.py
"""

import os
import csv
import torch
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from config import STANCE_MODEL_DIR, STANCE_LABELS, DATA_DIR


def evaluate():
    """Evaluate the trained stance classifier on the test set."""

    print("=" * 50)
    print("  STANCE FIRMNESS CLASSIFIER — EVALUATION")
    print("=" * 50 + "\n")

    # Load model
    if not os.path.exists(STANCE_MODEL_DIR):
        raise FileNotFoundError(
            f"Model not found: {STANCE_MODEL_DIR}\n"
            f"Run 'python training/train_stance_model.py' first."
        )

    tokenizer = DistilBertTokenizer.from_pretrained(STANCE_MODEL_DIR)
    model = DistilBertForSequenceClassification.from_pretrained(STANCE_MODEL_DIR)
    model.eval()

    # Load data and get test split (same split as training)
    data_path = os.path.join(DATA_DIR, "cmv_labeled.csv")
    label_to_idx = {label: idx for idx, label in enumerate(STANCE_LABELS)}

    texts, labels = [], []
    with open(data_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["label"] in label_to_idx:
                texts.append(row["text"])
                labels.append(label_to_idx[row["label"]])

    # Reproduce the same split
    _, temp_texts, _, temp_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    _, test_texts, _, test_labels = train_test_split(
        temp_texts, temp_labels, test_size=0.5, random_state=42, stratify=temp_labels
    )

    # Predict
    print(f"Evaluating on {len(test_texts)} test examples...\n")
    predictions = []

    for text in test_texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        predictions.append(pred)

    # Metrics
    accuracy = accuracy_score(test_labels, predictions)
    print(f"Overall Accuracy: {accuracy:.3f} (target: 0.80+)\n")

    print("Classification Report:")
    print(classification_report(
        test_labels, predictions,
        target_names=STANCE_LABELS, digits=3
    ))

    print("Confusion Matrix:")
    cm = confusion_matrix(test_labels, predictions)
    print(f"{'':>25} {'Predicted':>10}")
    print(f"{'':>15}", end="")
    for label in STANCE_LABELS:
        print(f"{label[:8]:>10}", end="")
    print()
    for i, label in enumerate(STANCE_LABELS):
        print(f"{label:>15}", end="")
        for j in range(len(STANCE_LABELS)):
            print(f"{cm[i][j]:>10}", end="")
        print()

    # Check pass/fail
    print("\n" + "─" * 40)
    if accuracy >= 0.80:
        print("✅ PASS — Accuracy target met!")
    else:
        print("❌ FAIL — Accuracy below 80% target.")
        print("   Consider: more data, more epochs, or fixing label quality.")


if __name__ == "__main__":
    evaluate()
