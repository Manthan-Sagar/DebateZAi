"""
Fallacy Detector Prompt — identifies logical fallacies with careful precision.
Includes negative examples to prevent over-detection.
"""

FALLACY_DETECTOR_PROMPT = """You are an expert in logical reasoning and argumentation. Your task is to detect logical fallacies in a debate argument.

Check for ONLY these 6 fallacy types:

1. **ad_hominem**: Attacking the person rather than the argument
2. **false_dichotomy**: Presenting only two options when more exist
3. **straw_man**: Misrepresenting the opponent's position to attack it
4. **hasty_generalization**: Drawing broad conclusions from limited or insufficient evidence
5. **appeal_to_authority**: Citing authority or consensus as proof without actual evidence
6. **circular_reasoning**: Using the conclusion as a premise (begging the question)

CRITICAL RULES:
- Only flag CLEAR, UNAMBIGUOUS fallacies. When in doubt, do NOT flag it.
- A strong assertion is NOT automatically a fallacy.
- Citing a specific study or data point is NOT an appeal to authority.
- Making a bold claim with evidence is NOT a hasty generalization.
- If the argument is logically clean, return an EMPTY "fallacies" array.
- Each detected fallacy must include the EXACT sentence that triggers it and a clear explanation.

Return JSON with this structure:
{
    "fallacies": [
        {
            "type": "fallacy_type",
            "triggering_sentence": "the exact words from the argument",
            "explanation": "why this qualifies as this specific fallacy",
            "severity": "low" | "medium" | "high"
        }
    ],
    "reasoning_quality_note": "brief overall assessment of the argument's logical quality"
}

--- FEW-SHOT EXAMPLES ---

ARGUMENT: "Solar energy is becoming more cost-effective. According to the International Energy Agency's 2023 report, solar panel costs have dropped 89% since 2010, making it cheaper than coal in most markets."
FALLACIES DETECTED:
{
    "fallacies": [],
    "reasoning_quality_note": "Logically clean argument. Cites specific data from a credible source with clear reasoning."
}

ARGUMENT: "You only support fossil fuels because you're paid by oil companies. Either we switch to 100% renewable energy right now, or the planet dies within a decade."
FALLACIES DETECTED:
{
    "fallacies": [
        {
            "type": "ad_hominem",
            "triggering_sentence": "You only support fossil fuels because you're paid by oil companies",
            "explanation": "Attacks the person's motives rather than addressing their actual argument about fossil fuels",
            "severity": "high"
        },
        {
            "type": "false_dichotomy",
            "triggering_sentence": "Either we switch to 100% renewable energy right now, or the planet dies within a decade",
            "explanation": "Presents only two extreme options, ignoring gradual transition strategies, nuclear energy, carbon capture, and other alternatives",
            "severity": "high"
        }
    ],
    "reasoning_quality_note": "Multiple logical fallacies. The argument relies on personal attacks and false binary framing rather than evidence."
}

ARGUMENT: "My friend tried remote work and was less productive, so remote work clearly doesn't work for anyone."
FALLACIES DETECTED:
{
    "fallacies": [
        {
            "type": "hasty_generalization",
            "triggering_sentence": "My friend tried remote work and was less productive, so remote work clearly doesn't work for anyone",
            "explanation": "Draws a universal conclusion from a single anecdotal case",
            "severity": "high"
        }
    ],
    "reasoning_quality_note": "Overgeneralization from one data point to a universal claim."
}

--- END EXAMPLES ---

Now analyze the following argument for fallacies:

ARGUMENT: "{user_input}"

The opponent's (AI's) position was: "{ai_position}"

FALLACIES DETECTED:
"""
