"""
Adaptive Question Engine Prompt — generates probing questions that target conceptual gaps.
"""

CONCEPT_GRAPH_PROMPT = """You are an expert in the topic: "{topic}"

Generate a concept graph for this topic — a structured map of key concepts, sub-concepts, and their relationships. This will be used to probe a debater's understanding.

Return a JSON object with:
- "concepts": a list of concept objects, each with:
  - "id": unique short identifier
  - "name": concept name
  - "level": "foundational" | "intermediate" | "advanced"
  - "depends_on": list of concept IDs this concept requires understanding of
  - "description": one-sentence description

Include 8-12 concepts covering the full depth of the topic, from foundational to advanced.

IMPORTANT: Return ONLY valid JSON.

Example for "Universal Basic Income":
{{
    "concepts": [
        {{"id": "income_dist", "name": "Income Distribution", "level": "foundational", "depends_on": [], "description": "How wealth and income are distributed across a population"}},
        {{"id": "poverty_line", "name": "Poverty Line Mechanics", "level": "foundational", "depends_on": ["income_dist"], "description": "How poverty thresholds are defined and measured"}},
        {{"id": "fiscal_policy", "name": "Government Fiscal Policy", "level": "intermediate", "depends_on": ["income_dist"], "description": "How governments raise and spend money"}},
        {{"id": "inflation", "name": "Inflationary Effects", "level": "advanced", "depends_on": ["fiscal_policy"], "description": "How injecting money into an economy affects price levels"}}
    ]
}}

Now generate the concept graph for: "{topic}"
"""

ADAPTIVE_QUESTION_PROMPT = """You are a debate evaluator probing a user's understanding of: "{topic}"

Based on the debate so far, generate a targeted probing question.

CONCEPT GRAPH:
{concept_graph}

CONCEPTS ALREADY DEMONSTRATED:
{demonstrated_concepts}

CONCEPTS WEAK OR AVOIDED:
{weak_concepts}

FALLACIES COMMITTED:
{fallacies_committed}

USER'S CURRENT PERFORMANCE LEVEL: {performance_level}
(Scale: "struggling" → "basic" → "competent" → "strong" → "expert")

QUESTION GENERATION RULES:
1. If user argued confidently about X but never addressed Y (which X depends on) → ask about Y
2. If user made a claim that requires knowing Z → ask them to defend Z specifically
3. If user committed a fallacy → probe whether it was intentional rhetoric or genuine misunderstanding
4. If performance is "struggling" or "basic" → ask a foundational question
5. If performance is "competent" or higher → ask about relationships between concepts

DEBATE HISTORY:
{debate_history}

Return JSON:
{{
    "question": "Your probing question here",
    "target_concept": "concept_id being probed",
    "difficulty": "foundational" | "intermediate" | "advanced",
    "rationale": "Why this question targets the user's specific gap"
}}

IMPORTANT: Return ONLY valid JSON.
"""
