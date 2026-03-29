"""
Module 5 — Consistency Tracker
Tracks all positions taken by both AI and user across the debate.
Detects contradictions vs refinements before generating new responses.
"""

from gemini_client import call_gemini


class ConsistencyTracker:
    """
    Maintains a running log of all positions taken during the debate.
    Distinguishes between genuine contradictions and argument refinements.
    """

    def __init__(self):
        self.ai_positions = []       # List of positions/claims AI has made
        self.user_positions = []     # List of positions/claims user has made
        self.ai_concessions = []     # Points the AI has conceded
        self.user_concessions = []   # Points the user has conceded
        self.contradictions_found = []  # Log of detected contradictions
        self.refinements_found = []    # Log of detected refinements

    def record_ai_position(self, position: str):
        """Record a position the AI has taken."""
        self.ai_positions.append(position)

    def record_user_position(self, main_claim: str, premises: list):
        """Record the user's stated positions from parsed argument."""
        self.user_positions.append({
            "claim": main_claim,
            "premises": premises,
        })

    def record_concession(self, role: str, concession: str):
        """Record a concession made by either party."""
        if role == "ai":
            self.ai_concessions.append(concession)
        else:
            self.user_concessions.append(concession)

    def check_ai_consistency(self, proposed_rebuttal: str) -> dict:
        """
        Check if a proposed AI rebuttal contradicts any prior AI positions.

        Returns:
            dict with "is_consistent" bool and "conflict_details" if inconsistent.
        """
        if not self.ai_positions:
            return {"is_consistent": True, "conflict_details": None}

        prompt = f"""Check if the following proposed statement contradicts any of the previously stated positions.

PROPOSED STATEMENT:
{proposed_rebuttal}

PREVIOUS POSITIONS:
{chr(10).join(f'- {p}' for p in self.ai_positions)}

PREVIOUS CONCESSIONS:
{chr(10).join(f'- {c}' for c in self.ai_concessions) if self.ai_concessions else 'None'}

Return JSON:
{{
    "is_consistent": true/false,
    "conflict_details": "explanation of the contradiction" or null
}}

Return ONLY valid JSON.
"""
        return call_gemini(prompt, expect_json=True)

    def check_user_consistency(self, new_argument: dict) -> dict:
        """
        Check if the user's new argument contradicts their prior positions.
        Distinguishes between genuine contradictions and natural argument refinements.

        Returns:
            dict with "change_type" (consistent/refinement/contradiction) and details.
        """
        if not self.user_positions:
            return {"is_consistent": True, "change_type": "consistent", "contradiction": None}

        prompt = f"""You are an expert debate analyst. Classify HOW the user's new argument relates to their previous positions.

NEW ARGUMENT:
Claim: {new_argument.get('claim', '')}
Premises: {new_argument.get('premises', [])}

PREVIOUS POSITIONS:
{chr(10).join(f'- Claim: {p["claim"]}, Premises: {p["premises"]}' for p in self.user_positions)}

Classify the relationship as ONE of:
1. "consistent" — The new argument aligns with or continues the same line of reasoning.
2. "refinement" — The user is narrowing, deepening, or adding nuance to their previous position. This is NOT a contradiction. Examples: going from "AI is bad" to "AI creates systemic risks" is a refinement, not a contradiction.
3. "contradiction" — The user is genuinely taking an OPPOSITE stance to something they previously said. Example: saying "AI will destroy all jobs" then later saying "AI won't affect employment at all."

CRITICAL: Most argument evolution in a debate is "consistent" or "refinement". Only flag "contradiction" for genuine 180-degree reversals.

Return JSON:
{{
    "change_type": "consistent" or "refinement" or "contradiction",
    "explanation": "brief explanation of the relationship"
}}

Return ONLY valid JSON.
"""
        result = call_gemini(prompt, expect_json=True)

        change_type = result.get("change_type", "consistent")

        if change_type == "contradiction":
            self.contradictions_found.append(result.get("explanation", ""))
            return {
                "is_consistent": False,
                "change_type": "contradiction",
                "contradiction": result.get("explanation", ""),
            }
        elif change_type == "refinement":
            self.refinements_found.append(result.get("explanation", ""))
            return {
                "is_consistent": True,
                "change_type": "refinement",
                "contradiction": None,
            }
        else:
            return {
                "is_consistent": True,
                "change_type": "consistent",
                "contradiction": None,
            }

    def get_context_for_prompt(self) -> str:
        """Format the full consistency context to inject into Gemini prompts."""
        lines = ["=== CONSISTENCY CONTEXT ==="]
        lines.append(f"AI positions taken: {len(self.ai_positions)}")
        for i, pos in enumerate(self.ai_positions):
            lines.append(f"  AI-{i+1}: {pos}")
        lines.append(f"User contradictions found: {len(self.contradictions_found)}")
        for c in self.contradictions_found:
            lines.append(f"  ⚠ {c}")
        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Return summary for the mastery evaluator."""
        return {
            "user_positions_count": len(self.user_positions),
            "user_contradictions": self.contradictions_found,
            "user_refinements": self.refinements_found,
            "user_concessions": self.user_concessions,
            "ai_positions_count": len(self.ai_positions),
        }
