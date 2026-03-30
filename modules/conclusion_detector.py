"""
Module to detect if the user wants to conclude the debate early.
"""

from gemini_client import call_gemini

def check_if_concluding(user_input: str) -> bool:
    """
    Query the LLM to determine if the user's input indicates they are 
    done debating, conceding, or explicitly wanting to move on.
    """
    prompt = f"""You are an expert debate moderator analyzer.
Your task is to determine if the user's latest statement in a debate session is an explicit request to CONCLUDE or FINISH the conversation, OR a clear CONCESSION that ends the discussion.

CRITICALLY: 
A "conclusion" is NOT just a strong argument, a summary of a point, or a regular rebuttal. 
It MUST be an indication that the user wants to STOP the current process and move to the results.

EXAMPLES OF CONCLUSIONS (is_concluding: true):
- "I rest my case."
- "I'm done debating, let's see the report."
- "Okay, you've convinced me. Proceed."
- "That's all I have to say on this topic."
- "Let's wrap this up now."
- "I don't wish to continue this argument."

EXAMPLES OF NON-CONCLUSIONS (is_concluding: false):
- "In conclusion, my point about safety stands." (This is just a summarizing argument)
- "So you see, your logic is flawed." (Regular rebuttal)
- "I disagree because of X, Y, and Z." (Regular argument)
- "Can you explain that further?" (Request for info, not stopping)
- "But what about the financial impact?" (Moving to a new sub-point)

User statement: "{user_input}"

Return ONLY valid JSON with a single boolean key "is_concluding":
{{"is_concluding": true}} or {{"is_concluding": false}}
"""
    try:
        result = call_gemini(prompt, expect_json=True)
        return result.get("is_concluding", False)
    except Exception:
        return False
