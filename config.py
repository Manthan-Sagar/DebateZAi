"""
Central configuration for the AI Debate Partner system.
All constants, model paths, and API settings live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# LLM Backend Selection
# Set LLM_BACKEND in .env to switch between providers:
#   "gemini"  → Google Gemini API (rate-limited on free tier)
#   "ollama"  → Local Ollama server (unlimited, good for debugging)
#   "groq"    → Groq API (hyper-fast open source models)
# ──────────────────────────────────────────────
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")  # Default to ollama for dev

# ──────────────────────────────────────────────
# Gemini API
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.7

# ──────────────────────────────────────────────
# Ollama (Local LLM)
# ──────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TEMPERATURE = 0.7

# ──────────────────────────────────────────────
# Groq API (Ultra-fast cloud LLM)
# ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.7

# ──────────────────────────────────────────────
# Shared LLM Settings
# ──────────────────────────────────────────────
LLM_MAX_RETRIES = 3                        # Retries on JSON parse failure

# ──────────────────────────────────────────────
# Session Settings
# ──────────────────────────────────────────────
DEBATE_TURNS = 8          # Number of turns in Phase 1 (Debate Mode)
PROBE_TURNS = 6           # Number of turns in Phase 2 (Probe Mode)
MAX_RESPONSE_TIME_SEC = 5 # Target max response time per AI turn

# ──────────────────────────────────────────────
# Stance Classifier (DistilBERT)
# ──────────────────────────────────────────────
STANCE_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "stance_model")
STANCE_LABELS = ["new_argument", "restatement", "emotional_pressure", "concession_with_reasoning"]
STANCE_MODEL_NAME = "distilbert-base-uncased"

# ──────────────────────────────────────────────
# Fallacy Detection
# ──────────────────────────────────────────────
FALLACY_TYPES = [
    "ad_hominem",
    "false_dichotomy",
    "straw_man",
    "hasty_generalization",
    "appeal_to_authority",
    "circular_reasoning",
]

# ──────────────────────────────────────────────
# Weakness Scoring Dimensions
# ──────────────────────────────────────────────
VULNERABILITY_DIMENSIONS = ["evidence", "scope", "causality"]

# ──────────────────────────────────────────────
# Rebuttal Strategies
# ──────────────────────────────────────────────
REBUTTAL_STRATEGIES = {
    "evidence":  "counterevidence",     # "Studies show X contradicts your premise"
    "scope":     "scope_reduction",     # "True in some cases, but not universally"
    "causality": "causal_challenge",    # "You haven't shown A causes B"
}

# Strategic modes — used when the user's argument is strong
STRATEGIC_MODES = ["reframe", "concede_and_pivot"]

# ──────────────────────────────────────────────
# Reddit / PRAW (for CMV data collection)
# ──────────────────────────────────────────────
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "AiDebaterSystem/1.0")

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
