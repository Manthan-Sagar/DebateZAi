"""
Module 6 — Stance Firmness Classifier
Classifies user pushback into 4 types to control AI response behavior.

Two modes:
1. Fine-tuned DistilBERT (preferred, requires training)
2. Gemini-prompted fallback (works without training data)
"""

import os
from config import STANCE_MODEL_DIR, STANCE_LABELS


def classify_stance_gemini(user_input: str, conversation_history: list) -> str:
    """
    Fallback: Use Gemini to classify pushback type.
    Used when the fine-tuned DistilBERT model is not available.

    Returns:
        One of: "new_argument", "restatement", "emotional_pressure", "concession_with_reasoning"
    """
    from gemini_client import call_gemini

    history_str = "\n".join(
        f"{'User' if t['role'] == 'user' else 'AI'}: {t['content']}"
        for t in conversation_history[-4:]
    ) if conversation_history else "(First turn)"

    prompt = f"""Classify the following debate response into exactly one category:

1. "new_argument" — The user introduces a genuinely new point not previously addressed
2. "restatement" — The user restates their previous point more forcefully but adds no new reasoning
3. "emotional_pressure" — The user expresses frustration or applies emotional pressure without new logic
4. "concession_with_reasoning" — The user acknowledges the opponent's point while defending their overall position

RECENT CONVERSATION:
{history_str}

CURRENT USER RESPONSE:
{user_input}

Return JSON:
{{"stance_type": "one_of_the_four_categories", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}

Return ONLY valid JSON.
"""
    result = call_gemini(prompt, expect_json=True)
    return result.get("stance_type", "new_argument")


# Global variables for lazy loading
_model = None
_tokenizer = None

def _load_model():
    """Lazily load the DistilBERT model and tokenizer into memory once."""
    global _model, _tokenizer
    if _model is None:
        import torch
        from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
        
        # Load exactly once into process memory
        _tokenizer = DistilBertTokenizer.from_pretrained(STANCE_MODEL_DIR)
        _model = DistilBertForSequenceClassification.from_pretrained(STANCE_MODEL_DIR)
        _model.eval()

def classify_stance_distilbert(user_input: str) -> str:
    """
    Primary: Use fine-tuned DistilBERT model for stance classification.
    Only works after training/train_stance_model.py has been run.

    Returns:
        One of: "new_argument", "restatement", "emotional_pressure", "concession_with_reasoning"
    """
    try:
        import torch
        
        # Load the model if it hasn't been loaded yet
        _load_model()

        inputs = _tokenizer(user_input, return_tensors="pt", truncation=True, max_length=256)

        with torch.no_grad():
            outputs = _model(**inputs)
            predicted_class = torch.argmax(outputs.logits, dim=1).item()

        return STANCE_LABELS[predicted_class]

    except Exception:
        # Model not trained yet — fall back to Gemini
        return None


def classify_stance(user_input: str, conversation_history: list = None) -> str:
    """
    Main entry point — tries DistilBERT first, falls back to Gemini.

    Returns:
        One of: "new_argument", "restatement", "emotional_pressure", "concession_with_reasoning"
    """
    # Try fine-tuned model first
    if os.path.exists(STANCE_MODEL_DIR):
        result = classify_stance_distilbert(user_input)
        if result:
            return result

    # Fallback to Gemini
    return classify_stance_gemini(user_input, conversation_history or [])
