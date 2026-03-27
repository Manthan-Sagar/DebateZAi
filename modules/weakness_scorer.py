"""
Module 2 — Weakness Scorer
Scores each premise on evidence, scope, and causality vulnerability.
The premise with the highest combined score gets attacked first.
"""

import json
from gemini_client import call_gemini
from prompts.weakness_scorer import WEAKNESS_SCORER_PROMPT
from config import REBUTTAL_STRATEGIES


def score_weaknesses(parsed_argument: dict, topic: str) -> dict:
    """
    Score each premise's vulnerability across 3 dimensions.

    Args:
        parsed_argument: Output from argument_parser.parse_argument()
        topic: The debate topic string.

    Returns:
        dict with scored_premises list and most_vulnerable_premise_index.
    """
    prompt = WEAKNESS_SCORER_PROMPT.format(
        topic=topic,
        main_claim=parsed_argument["main_claim"],
        premises=json.dumps(parsed_argument["premises"]),
        evidence_cited=json.dumps(parsed_argument["evidence_cited"]),
    )

    result = call_gemini(prompt, expect_json=True)

    # Ensure required fields
    if "scored_premises" not in result:
        result["scored_premises"] = []
    if "most_vulnerable_premise_index" not in result:
        # Fallback: pick the premise with highest total score
        if result["scored_premises"]:
            max_idx = max(
                range(len(result["scored_premises"])),
                key=lambda i: result["scored_premises"][i].get("total_vulnerability", 0)
            )
            result["most_vulnerable_premise_index"] = max_idx
        else:
            result["most_vulnerable_premise_index"] = 0

    return result


def get_attack_strategy(scored_premises: list, target_index: int) -> str:
    """
    Determine which rebuttal strategy to use based on the highest vulnerability dimension.

    Returns:
        One of: "counterevidence", "scope_reduction", "causal_challenge"
    """
    if not scored_premises or target_index >= len(scored_premises):
        return "counterevidence"  # default

    target = scored_premises[target_index]
    dimension = target.get("most_vulnerable_dimension", "evidence")

    return REBUTTAL_STRATEGIES.get(dimension, "counterevidence")
