"""
Module 3 — Fallacy Detector
Identifies logical fallacies in the user's argument.
Carefully calibrated to prevent over-detection.
"""

from gemini_client import call_gemini
from prompts.fallacy_detector import FALLACY_DETECTOR_PROMPT


def detect_fallacies(user_input: str, ai_position: str) -> dict:
    """
    Detect logical fallacies in the user's argument.

    Args:
        user_input: Raw text from the user's debate turn.
        ai_position: The AI's assigned position (for straw man detection).

    Returns:
        dict with "fallacies" list and "reasoning_quality_note" string.
    """
    prompt = FALLACY_DETECTOR_PROMPT.replace("{user_input}", user_input).replace("{ai_position}", ai_position)

    result = call_gemini(prompt, expect_json=True)

    # Ensure required fields
    if "fallacies" not in result:
        result["fallacies"] = []
    if "reasoning_quality_note" not in result:
        result["reasoning_quality_note"] = ""

    # Normalize each fallacy entry
    normalized = []
    for f in result["fallacies"]:
        if not isinstance(f, dict):
            continue
            
        score = f.get("confidence_score")
        if score is None:
            # Default to strong if the LLM forgot to include it
            score = 0.8
            
        try:
            score = float(score)
        except ValueError:
            score = 0.8
            
        if score < 0.6:
            continue  # Silently ignore low-confidence guesses
            
        normalized.append({
            "category": f.get("category", "soft").lower(),
            "type": f.get("type") or f.get("name") or "unknown",
            "confidence_score": score,
            "triggering_sentence": f.get("triggering_sentence") or f.get("sentence") or "",
            "explanation": f.get("explanation") or f.get("description") or "",
        })
    result["fallacies"] = normalized

    return result
