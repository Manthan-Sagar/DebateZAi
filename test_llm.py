"""Quick smoke test for LLM backend."""
from gemini_client import call_gemini

result = call_gemini(
    'Return a JSON object with a single key "status" and value "ok". Return ONLY valid JSON.',
    expect_json=True,
)
print("SUCCESS:", result)
