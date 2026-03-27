"""
Module 1 — Argument Parser
Extracts structured argument components from raw user input.
This is the most critical module — every downstream component depends on its output.
"""

import json
from gemini_client import call_gemini
from prompts.argument_parser import ARGUMENT_PARSER_PROMPT


def parse_argument(user_input: str) -> dict:
    """
    Parse a user's raw debate input into structured argument components.

    Args:
        user_input: Raw text from the user's debate turn.

    Returns:
        dict with keys: main_claim, premises, implicit_assumptions,
        evidence_cited, confidence_language
    """
    prompt = ARGUMENT_PARSER_PROMPT.replace("{user_input}", user_input)
    result = call_gemini(prompt, expect_json=True)

    # Validate expected fields exist
    required_fields = ["main_claim", "premises", "implicit_assumptions",
                       "evidence_cited", "confidence_language"]
    for field in required_fields:
        if field not in result:
            result[field] = [] if field in ("premises", "implicit_assumptions", "evidence_cited") else ""

    # Ensure premises is always a list
    if isinstance(result["premises"], str):
        result["premises"] = [result["premises"]]

    return result
