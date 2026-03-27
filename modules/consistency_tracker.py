"""
Module 5 — Consistency Tracker
Tracks all positions taken by both AI and user across the debate.
Detects contradictions before generating new responses.
"""

from gemini_client import call_gemini


class ConsistencyTracker:
    """
    Maintains a running log of all positions taken during the debate.
    Checks for contradictions in both AI and user statements.
    """

    def __init__(self):
        self.ai_positions = []       # List of positions/claims AI has made
        self.user_positions = []     # List of positions/claims user has made
        self.ai_concessions = []     # Points the AI has conceded
        self.user_concessions = []   # Points the user has conceded
        self.contradictions_found = []  # Log of detected contradictions

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
        User contradictions are flagged as evaluation signals.

        Returns:
            dict with "is_consistent" bool and "contradiction" details.
        """
        if not self.user_positions:
            return {"is_consistent": True, "contradiction": None}

        prompt = f"""Check if the following new argument contradicts any previously stated positions by the same person.

NEW ARGUMENT:
Claim: {new_argument.get('claim', '')}
Premises: {new_argument.get('premises', [])}

PREVIOUS POSITIONS:
{chr(10).join(f'- Claim: {p["claim"]}, Premises: {p["premises"]}' for p in self.user_positions)}

Return JSON:
{{
    "is_consistent": true/false,
    "contradiction": "explanation of what contradicts what" or null
}}

Return ONLY valid JSON.
"""
        result = call_gemini(prompt, expect_json=True)

        if not result.get("is_consistent", True):
            self.contradictions_found.append(result.get("contradiction", ""))

        return result

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
            "user_concessions": self.user_concessions,
            "ai_positions_count": len(self.ai_positions),
        }
