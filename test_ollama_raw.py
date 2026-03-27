import sys
from prompts.argument_parser import ARGUMENT_PARSER_PROMPT
from gemini_client import _call_ollama_raw, _strip_code_fences
import json

user_input = "ai is going to be the demise of humanity... the basic neccessities of people is now in danger"
prompt = ARGUMENT_PARSER_PROMPT.replace("{user_input}", user_input)

print("--- SENDING PROMPT TO OLLAMA ---")
raw_output = _call_ollama_raw(prompt)
print("--- RAW OUTPUT ---")
print(raw_output)
print("--- STRIPPED ---")
stripped = _strip_code_fences(raw_output)
print(stripped)

try:
    data = json.loads(stripped)
    print("--- JSON PARSED SUCCESSFULLY ---")
except Exception as e:
    print(f"--- JSON PARSE FAILED: {e} ---")
