"""
Module 7 — Mastery Evaluator
Aggregates all signals across the debate session and produces
a structured concept mastery report.
"""

import json
import time
from gemini_client import call_gemini_text
from prompts.mastery_evaluator import MASTERY_EVALUATOR_PROMPT


class MasteryEvaluator:
    """
    Collects data throughout the session and generates the final mastery report.
    """

    def __init__(self, topic: str, user_position: str, ai_position: str):
        self.topic = topic
        self.user_position = user_position
        self.ai_position = ai_position
        self.session_start = time.time()
        self.turn_log = []                # Full log of every turn with all data
        self.fallacy_log = []             # All fallacies detected with turn numbers
        self.stance_counts = {
            "new_argument": 0,
            "restatement": 0,
            "emotional_pressure": 0,
            "concession_with_reasoning": 0,
        }

    def record_turn(self, turn_number: int, user_input: str, ai_response: str,
                     parsed_argument: dict, weakness_scores: dict,
                     fallacies: dict, stance_type: str):
        """Record all data from a single debate turn."""
        self.turn_log.append({
            "turn": turn_number,
            "user_input": user_input,
            "ai_response": ai_response,
            "parsed_argument": parsed_argument,
            "weakness_scores": weakness_scores,
            "fallacies": fallacies.get("fallacies", []),
            "stance_type": stance_type,
        })

        # Track fallacies
        for f in fallacies.get("fallacies", []):
            self.fallacy_log.append({
                "turn": turn_number,
                "type": f.get("type", ""),
                "sentence": f.get("triggering_sentence", ""),
            })

        # Track stance types
        if stance_type in self.stance_counts:
            self.stance_counts[stance_type] += 1

    def generate_report(self, concept_mastery_summary: dict) -> str:
        """
        Generate the final mastery report using all session data.

        Args:
            concept_mastery_summary: Output from AdaptiveEngine.get_mastery_summary()

        Returns:
            Formatted mastery report as string.
        """
        session_duration_min = round((time.time() - self.session_start) / 60)

        # Format fallacy summary
        if self.fallacy_log:
            fallacy_summary = "\n".join(
                f"  Turn {f['turn']}: {f['type']} — \"{f['sentence']}\""
                for f in self.fallacy_log
            )
        else:
            fallacy_summary = "No fallacies detected."

        prompt = MASTERY_EVALUATOR_PROMPT.format(
            topic=self.topic,
            user_position=self.user_position,
            ai_position=self.ai_position,
            total_turns=len(self.turn_log),
            session_duration=f"{session_duration_min} minutes",
            session_log=json.dumps(self.turn_log, indent=2),
            strong_concepts=json.dumps(concept_mastery_summary.get("demonstrated_strongly", [])),
            weak_concepts=json.dumps(concept_mastery_summary.get("demonstrated_weakly", [])),
            unaddressed_concepts=json.dumps(concept_mastery_summary.get("never_addressed", [])),
            fallacy_summary=fallacy_summary,
            new_argument_count=self.stance_counts["new_argument"],
            restatement_count=self.stance_counts["restatement"],
            emotional_count=self.stance_counts["emotional_pressure"],
            concession_count=self.stance_counts["concession_with_reasoning"],
        )

        return call_gemini_text(prompt)
