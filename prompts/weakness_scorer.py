"""
Weakness Scorer Prompt — scores each premise on 3 vulnerability dimensions.
"""

WEAKNESS_SCORER_PROMPT = """You are an expert debate analyst. Your task is to evaluate the logical vulnerability of each premise in an argument.

For each premise, score it on three dimensions (0.0 to 1.0):

1. **evidence_score**: How unsupported is this claim?
   - 0.0 = backed by strong, specific evidence
   - 0.5 = partially supported or anecdotal
   - 1.0 = pure assertion with no evidence at all

2. **scope_score**: How overgeneralized is this claim?
   - 0.0 = appropriately scoped (e.g., "some studies suggest")
   - 0.5 = moderate generalization (e.g., "most people")
   - 1.0 = extreme generalization (e.g., "all", "every", "always", "never")

3. **causality_score**: How weak is the causal reasoning?
   - 0.0 = well-established causal link with mechanism explained
   - 0.5 = correlation implied but causation not proven
   - 1.0 = pure correlation presented as causation, or no causal link at all

Return a JSON object with a "scored_premises" array. Each item should have:
- "premise": the exact premise text
- "evidence_score": float 0-1
- "scope_score": float 0-1
- "causality_score": float 0-1
- "total_vulnerability": sum of all three scores (0-3)
- "most_vulnerable_dimension": which dimension scored highest
- "reasoning": brief explanation of why this premise is vulnerable

Also include "most_vulnerable_premise_index" (0-indexed) indicating which premise to attack first.

IMPORTANT: Return ONLY valid JSON.

--- CONTEXT ---

Topic: {topic}
Main Claim: {main_claim}
Premises: {premises}
Evidence Cited: {evidence_cited}

--- OUTPUT ---
"""
