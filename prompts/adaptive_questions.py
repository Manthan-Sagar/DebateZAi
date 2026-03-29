"""
Adaptive Question Engine Prompts — generates probing questions and evaluates answers.
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

Based on the debate so far, generate a single, strict probing question that evaluates their knowledge.

CRITICAL INSTRUCTIONS:
1. The question MUST be highly relevant to the main topic: "{topic}". Do not stray into unrelated tangents.
2. You MUST NOT ask any question that is conceptually identical or very similar to a previously asked question.
3. The difficulty of the question MUST specifically be: "{target_difficulty}". 
   - Foundational: Basic definitions, core premises, obvious facts.
   - Intermediate: Nuances, practical applications, counter-arguments.
   - Advanced: Edge cases, philosophical implications, complex systemic interactions.

CONCEPT GRAPH:
{concept_graph}

CONCEPTS ALREADY DEMONSTRATED:
{demonstrated_concepts}

PREVIOUSLY ASKED QUESTIONS (DO NOT REPEAT THESE):
{previously_asked_questions}

QUESTION GENERATION RULES:
1. If user argued confidently about X but never addressed Y (which X depends on) → ask about Y
2. If user made a claim that requires knowing Z → ask them to defend Z specifically
3. STRICTLY adhere to the requested "{target_difficulty}" level.

Return JSON:
{{
    "question": "Your probing question here",
    "target_concept": "concept_id being probed",
    "difficulty": "{target_difficulty}",
    "rationale": "Why this question targets the user's specific gap"
}}

IMPORTANT: Return ONLY valid JSON.
"""

ADAPTIVE_EVALUATION_PROMPT = """You are an expert, tolerant, and humane grader evaluating a user's answer to a knowledge test question on the topic: "{topic}".

QUESTION ASKED: "{question}"
USER'S ANSWER: "{user_input}"

Your task is to grade their answer out of 10 based on the following Strict but Fair Rubric:
- 0 to 2: The user explicitly states "I don't know", the answer is completely off-topic, or it is fundamentally wrong.
- 3 to 5: The user made a basic attempt but lacked serious depth or missed core concepts.
- 6 to 8: Good understanding! The user hit the main points but missed some nuances or advanced implications.
- 9 to 10: Perfect, comprehensive, and nuanced answer covering all angles.

CRITICAL INSTRUCTION: Do not just point out flaws. Act as a helpful teacher. Explicitly state what they got right, and exactly what specific knowledge they need to add.

Return ONLY valid JSON in this exact format:
{{
    "score": <number between 0 and 10>,
    "what_was_good": "2-3 sentences explaining exactly what aspects of their answer were correct or well-reasoned.",
    "what_to_add": "2-3 sentences explaining exactly what knowledge or nuance was lacking, and what they should add to improve."
}}
"""
