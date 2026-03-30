"""
DistilBERT Fine-Tuning Script for Stance Firmness Classification.
Trains a 4-class classifier on labeled CMV data.

Usage:
    python training/train_stance_model.py

Expected: ~20-40 minutes on a mid-range GPU.
"""

import os
import csv
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch.nn as nn

class WeightedTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        if self.class_weights is not None:
            loss_fct = nn.CrossEntropyLoss(weight=self.class_weights.to(model.device))
        else:
            loss_fct = nn.CrossEntropyLoss()
        
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss
from torch.utils.data import Dataset

from config import STANCE_MODEL_DIR, STANCE_LABELS, STANCE_MODEL_NAME, DATA_DIR


class StanceDataset(Dataset):
    """PyTorch dataset for stance classification."""

    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.encodings = tokenizer(
            texts, truncation=True, padding=True,
            max_length=max_length, return_tensors="pt"
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def load_data():
    """Load labeled CMV data from CSV."""
    data_path = os.path.join(DATA_DIR, "cmv_labeled.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Data file not found: {data_path}\n"
            f"Run 'python training/collect_cmv_data.py' first."
        )

    texts, labels = [], []
    label_to_idx = {label: idx for idx, label in enumerate(STANCE_LABELS)}

    with open(data_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["label"] in label_to_idx:
                texts.append(row["text"])
                labels.append(label_to_idx[row["label"]])

    print(f"Loaded {len(texts)} examples")
    for label, idx in label_to_idx.items():
        count = labels.count(idx)
        print(f"  {label}: {count}")

    return texts, labels


def train():
    """Fine-tune DistilBERT on stance classification data."""

    print("=" * 50)
    print("  STANCE FIRMNESS CLASSIFIER — TRAINING")
    print("=" * 50 + "\n")

    # Load data
    texts, labels = load_data()

    # Split into train / eval / test
    train_texts, temp_texts, train_labels, temp_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    eval_texts, test_texts, eval_labels, test_labels = train_test_split(
        temp_texts, temp_labels, test_size=0.5, random_state=42
    )

    print(f"\nSplit: {len(train_texts)} train / {len(eval_texts)} eval / {len(test_texts)} test\n")

    # Load tokenizer and model
    tokenizer = DistilBertTokenizer.from_pretrained(STANCE_MODEL_NAME)
    model = DistilBertForSequenceClassification.from_pretrained(
        STANCE_MODEL_NAME, num_labels=len(STANCE_LABELS)
    )

    # Create datasets
    train_dataset = StanceDataset(train_texts, train_labels, tokenizer)
    eval_dataset = StanceDataset(eval_texts, eval_labels, tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=STANCE_MODEL_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        warmup_steps=200,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=50,
        report_to="none",  # Disable wandb etc.
    )

    # Calculate class weights for imbalance
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.unique(train_labels)
    weights = compute_class_weight('balanced', classes=classes, y=train_labels)
    full_weights = np.ones(len(STANCE_LABELS), dtype=np.float32)
    for cls, w in zip(classes, weights):
        full_weights[cls] = w
    class_weights_tensor = torch.tensor(full_weights, dtype=torch.float32)

    # Train
    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        class_weights=class_weights_tensor
    )

    print("🚀 Starting training...")
    trainer.train()

    # Save model and tokenizer
    os.makedirs(STANCE_MODEL_DIR, exist_ok=True)
    model.save_pretrained(STANCE_MODEL_DIR)
    tokenizer.save_pretrained(STANCE_MODEL_DIR)
    print(f"\n✅ Model saved to {STANCE_MODEL_DIR}")

    # Quantize for fast CPU inference
    print("\n⚡ Quantizing model for CPU inference...")
    quantized_model = torch.quantization.quantize_dynamic(
        model, {torch.nn.Linear}, dtype=torch.qint8
    )
    quantized_path = os.path.join(STANCE_MODEL_DIR, "stance_model_quantized.pt")
    torch.save(quantized_model.state_dict(), quantized_path)
    print(f"✅ Quantized model saved to {quantized_path}")

    return model, tokenizer, test_texts, test_labels


if __name__ == "__main__":
    train()
