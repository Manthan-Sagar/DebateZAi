"""
Core LLM client — the backbone of the entire system.
Supports two backends:
  1. Gemini API  (cloud, rate-limited on free tier)
  2. Ollama      (local, unlimited, great for debugging)

Switch via LLM_BACKEND in .env ("gemini" or "ollama").
"""

import json
import time
import requests
from config import (
    LLM_BACKEND, LLM_MAX_RETRIES,
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE,
    OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE,
)


# ──────────────────────────────────────────────
# Backend initialization
# ──────────────────────────────────────────────
_gemini_model = None

if LLM_BACKEND == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config=genai.GenerationConfig(
            temperature=GEMINI_TEMPERATURE,
        ),
    )
    print(f"LLM Backend: Gemini ({GEMINI_MODEL})")
else:
    print(f"LLM Backend: Ollama ({OLLAMA_MODEL} @ {OLLAMA_BASE_URL})")


# ──────────────────────────────────────────────
# Low-level backend calls
# ──────────────────────────────────────────────

def _call_gemini_raw(prompt: str, expect_json: bool = False) -> str:
    """Send prompt to Gemini API and return raw text."""
    response = _gemini_model.generate_content(prompt)
    return response.text.strip()


def _call_ollama_raw(prompt: str, expect_json: bool = False) -> str:
    """Send prompt to local Ollama server and return raw text."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1 if expect_json else OLLAMA_TEMPERATURE,  # Lower temp for more reliable JSON
            "num_predict": -1,   # Unlimited tokens
        },
    }
    if expect_json:
        payload["format"] = "json"

    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["response"].strip()
    except requests.ConnectionError:
        raise ConnectionError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            f"Make sure Ollama is running: 'ollama serve'"
        )
    except requests.Timeout:
        raise TimeoutError(
            f"Ollama request timed out after 120s. "
            f"Your model ({OLLAMA_MODEL}) may be too slow for this prompt."
        )


def _call_llm_raw(prompt: str, expect_json: bool = False) -> str:
    """Route to the active backend."""
    if LLM_BACKEND == "gemini":
        return _call_gemini_raw(prompt, expect_json)
    else:
        return _call_ollama_raw(prompt, expect_json)


# ──────────────────────────────────────────────
# Public API (used by all modules)
# ──────────────────────────────────────────────

def call_gemini(prompt: str, expect_json: bool = True) -> dict | str:
    """
    Send a prompt to the active LLM backend and return the response.
    (Function name kept as call_gemini for backward compatibility.)

    Args:
        prompt: The full prompt string (including few-shot examples).
        expect_json: If True, parse response as JSON with retry logic.
                     If False, return raw text (used for rebuttals / reports).

    Returns:
        Parsed dict if expect_json=True, raw string otherwise.

    Raises:
        ValueError: If JSON parsing fails after all retries.
    """
    last_error = None

    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            text = _call_llm_raw(prompt, expect_json)

            if not expect_json:
                return text

            # ── Strip markdown code fences if LLM wraps output ──
            json_text = _strip_code_fences(text)
            return json.loads(json_text)

        except json.JSONDecodeError as e:
            last_error = e
            if attempt < LLM_MAX_RETRIES:
                # Retry with a stricter suffix
                prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No preamble, no explanation, no markdown formatting."
                time.sleep(0.5)
            continue

        except Exception as e:
            last_error = e
            if attempt < LLM_MAX_RETRIES:
                time.sleep(1)
            continue

    raise ValueError(
        f"LLM call failed after {LLM_MAX_RETRIES} attempts. "
        f"Backend: {LLM_BACKEND} | Last error: {last_error}"
    )


def call_gemini_text(prompt: str) -> str:
    """Convenience wrapper — always returns raw text, never parses JSON."""
    return call_gemini(prompt, expect_json=False)


def _strip_code_fences(text: str) -> str:
    """
    Strip markdown code fences that LLMs sometimes wrap around JSON.
    Handles: ```json { ... } ```, ``` { ... } ```, etc.
    """
    if LLM_BACKEND == "ollama":
        import re
        # Local LLMs often add preambles: "Here is your JSON: ```json ... ```"
        match = re.search(r"```(?:json|JSON)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        # Fallback 1: Extract anything between the first { and last }
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1:
            if end_idx != -1 and end_idx > start_idx:
                return text[start_idx:end_idx+1]
            else:
                # Llama 3 frequently forgets the final closing brace. Patch it.
                return text[start_idx:] + "\n}"
            
        return text.strip()

    # --- Original Gemini Logic (Untouched) ---
    if text.startswith("```"):
        lines = text.split("```")
        # The actual content is between the first and second ```
        if len(lines) >= 2:
            content = lines[1]
            # Remove the language identifier (e.g., "json")
            if content.startswith("json"):
                content = content[4:]
            elif content.startswith("JSON"):
                content = content[4:]
            return content.strip()
    return text
