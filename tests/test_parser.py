"""
Tests for the Argument Parser module.
Run: python -m pytest tests/test_parser.py -v
"""

import json
import os
import pytest

# Test data path
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "test_arguments.json")


def load_test_arguments():
    """Load test arguments from JSON file."""
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestArgumentParser:
    """Tests for argument parser module."""

    # NOTE: These tests require a valid GEMINI_API_KEY in .env
    # They make actual API calls — run sparingly during development

    @pytest.fixture
    def parser(self):
        from modules.argument_parser import parse_argument
        return parse_argument

    def test_output_has_required_fields(self, parser):
        """Parser output must contain all required fields."""
        result = parser("Social media should be banned for kids because it causes depression.")
        required = ["main_claim", "premises", "implicit_assumptions",
                     "evidence_cited", "confidence_language"]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_premises_is_list(self, parser):
        """Premises should always be a list."""
        result = parser("Nuclear energy is safe and efficient.")
        assert isinstance(result["premises"], list)

    def test_evidence_is_list(self, parser):
        """Evidence cited should always be a list."""
        result = parser("According to WHO, processed meat increases cancer risk.")
        assert isinstance(result["evidence_cited"], list)

    def test_confidence_is_valid(self, parser):
        """Confidence language should be high, medium, or low."""
        result = parser("This is obviously true and everyone knows it.")
        assert result["confidence_language"] in ("high", "medium", "low")

    def test_multiple_premises_extracted(self, parser):
        """Parser should NOT collapse multiple premises into one."""
        result = parser(
            "Social media should be banned for under-16s because "
            "it causes depression, reduces academic performance, "
            "and exposes children to cyberbullying."
        )
        assert len(result["premises"]) >= 2, \
            f"Expected 2+ premises, got {len(result['premises'])}: {result['premises']}"

    def test_edge_case_minimal_input(self, parser):
        """Parser should handle minimal input gracefully."""
        result = parser("Maybe.")
        assert "main_claim" in result
        # Should not crash on minimal input

    def test_evidence_detected(self, parser):
        """Parser should detect cited evidence."""
        result = parser(
            "According to a 2023 Stanford study, remote workers are 13% more productive. "
            "The BLS data also shows lower turnover rates."
        )
        assert len(result["evidence_cited"]) >= 1, \
            f"Expected evidence, got: {result['evidence_cited']}"

    def test_high_confidence_detection(self, parser):
        """Parser should flag overconfident language."""
        result = parser("This is obviously true. Everyone knows it. It's undeniable.")
        assert result["confidence_language"] == "high"

    def test_low_confidence_detection(self, parser):
        """Parser should detect hedging language."""
        result = parser("I'm not sure, but maybe this could possibly be an issue.")
        assert result["confidence_language"] == "low"
