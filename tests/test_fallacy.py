"""
Tests for the Fallacy Detector module.
Run: python -m pytest tests/test_fallacy.py -v
"""

import pytest


class TestFallacyDetector:
    """Tests for fallacy detection — especially over-detection prevention."""

    @pytest.fixture
    def detector(self):
        from modules.fallacy_detector import detect_fallacies
        return detect_fallacies

    def test_clean_argument_no_fallacies(self, detector):
        """A logically clean argument should return ZERO fallacies."""
        result = detector(
            "Solar energy costs have dropped 89% since 2010 according to the IEA. "
            "This makes it cheaper than coal in most markets, suggesting that "
            "economic incentives now favor renewable energy adoption.",
            ai_position="Renewable energy transition is too expensive."
        )
        assert len(result["fallacies"]) == 0, \
            f"Expected 0 fallacies on clean argument, got: {result['fallacies']}"

    def test_ad_hominem_detected(self, detector):
        """Should detect ad hominem attacks."""
        result = detector(
            "You only say that because you're uneducated. Someone like you "
            "clearly can't understand complex economic arguments.",
            ai_position="UBI is fiscally unsustainable."
        )
        fallacy_types = [f["type"] for f in result["fallacies"]]
        assert "ad_hominem" in fallacy_types

    def test_false_dichotomy_detected(self, detector):
        """Should detect false dichotomy."""
        result = detector(
            "Either we ban all fossil fuels immediately, or the entire planet "
            "will be destroyed within a decade. There is no middle ground.",
            ai_position="A gradual energy transition is more practical."
        )
        fallacy_types = [f["type"] for f in result["fallacies"]]
        assert "false_dichotomy" in fallacy_types

    def test_output_structure(self, detector):
        """Output should have the correct structure."""
        result = detector("Some argument.", ai_position="Counter position.")
        assert "fallacies" in result
        assert isinstance(result["fallacies"], list)
        assert "reasoning_quality_note" in result
