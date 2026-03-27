"""
Rebuttal Generator — generates targeted rebuttals using strategy selection.
Three strategies: counterevidence, scope_reduction, causal_challenge.
"""

import json
from gemini_client import call_gemini_text
from prompts.rebuttal_generator import REBUTTAL_GENERATOR_PROMPT, STANCE_INSTRUCTIONS


def generate_rebuttal(
    topic: str,
    ai_position: str,
    parsed_argument: dict,
    weakness_scores: dict,
    rebuttal_strategy: str,
    conversation_history: list,
    stance_type: str = "default",
) -> str:
    """
    Generate a targeted rebuttal for the user's argument.

    Args:
        topic: The debate topic.
        ai_position: AI's assigned position.
        parsed_argument: Output from argument_parser.
        weakness_scores: Output from weakness_scorer.
        rebuttal_strategy: One of "counterevidence", "scope_reduction", "causal_challenge".
        conversation_history: List of previous turns [{"role": "user"|"ai", "content": str}].
        stance_type: From stance classifier — "new_argument", "restatement", etc.

    Returns:
        The AI's rebuttal as a string.
    """
    # Get the target premise
    target_idx = weakness_scores.get("most_vulnerable_premise_index", 0)
    scored = weakness_scores.get("scored_premises", [])

    if scored and target_idx < len(scored):
        target_premise = scored[target_idx].get("premise", "")
        weakness_reasoning = scored[target_idx].get("reasoning", "")
    else:
        target_premise = parsed_argument["premises"][0] if parsed_argument["premises"] else ""
        weakness_reasoning = "This premise appears unsupported."

    # Format conversation history
    history_str = "\n".join(
        f"{'User' if turn['role'] == 'user' else 'AI'}: {turn['content']}"
        for turn in conversation_history[-6:]  # Last 6 turns for context
    ) if conversation_history else "(First turn)"

    # Get stance instruction
    stance_instruction = STANCE_INSTRUCTIONS.get(stance_type, STANCE_INSTRUCTIONS["default"])

    prompt = REBUTTAL_GENERATOR_PROMPT.format(
        ai_position=ai_position,
        rebuttal_strategy=rebuttal_strategy,
        target_premise=target_premise,
        weakness_reasoning=weakness_reasoning,
        topic=topic,
        main_claim=parsed_argument["main_claim"],
        argument_json=json.dumps(parsed_argument, indent=2),
        conversation_history=history_str,
        stance_instruction=stance_instruction,
    )

    return call_gemini_text(prompt)
