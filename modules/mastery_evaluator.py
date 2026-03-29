"""
Module 7 — Mastery Evaluator
Aggregates all signals across the session and produces
a mode-specific structured concept mastery report.
"""

import time
from gemini_client import call_gemini_text
from prompts.mastery_evaluator import DEBATE_REPORT_PROMPT, TEST_REPORT_PROMPT


class MasteryEvaluator:
    """
    Collects data throughout the session and generates the final report.
    """

    def __init__(self, topic: str, user_position: str, ai_position: str, mode: str = '1'):
        self.topic = topic
        self.user_position = user_position
        self.ai_position = ai_position
        self.mode = mode
        self.session_start = time.time()
        self.turn_log = []
        self.fallacy_log = []

    def record_turn(self, turn_number: int, user_input: str, ai_response: str,
                     parsed_argument: dict, weakness_scores: dict,
                     fallacies: dict, stance_type: str):
        """Record all data from a single debate turn."""
        self.turn_log.append({
            "turn": turn_number,
            "user_input": user_input,
            "ai_response": ai_response,
        })

        # Track fallacies
        for f in fallacies.get("fallacies", []):
            self.fallacy_log.append({
                "turn": turn_number,
                "type": f.get("type", ""),
                "sentence": f.get("triggering_sentence", ""),
            })

    def generate_report(self, concept_mastery_summary: dict = None) -> str:
        """
        Generate the final report using the specific Mode prompts.
        """
        # Format a clean, string-based log to avoid choking weak LLMs
        clean_log_lines = []
        for turn in self.turn_log:
            clean_log_lines.append(f"--- TURN {turn['turn']} ---")
            clean_log_lines.append(f"User: {turn['user_input']}")
            clean_log_lines.append(f"AI: {turn['ai_response']}\n")
            
        clean_session_log = "\n".join(clean_log_lines)

        if self.mode == '1': # Debate Mode
            prompt = DEBATE_REPORT_PROMPT.format(
                topic=self.topic,
                user_position=self.user_position,
                ai_position=self.ai_position,
                clean_session_log=clean_session_log,
            )
        else: # Knowledge Test Mode
            prompt = TEST_REPORT_PROMPT.format(
                topic=self.topic,
                clean_session_log=clean_session_log
            )

        try:
            return call_gemini_text(prompt)
        except Exception as e:
            return f"Error generating report: {e}\n\nPlease check your LLM backend connection."
