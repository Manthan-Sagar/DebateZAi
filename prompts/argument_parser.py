"""
Argument Parser Prompt — the most critical prompt in the system.
Extracts structured argument components from raw user input.

Output schema:
{
    "main_claim": str,
    "premises": [str, ...],
    "implicit_assumptions": [str, ...],
    "evidence_cited": [str, ...],
    "confidence_language": "high" | "medium" | "low"
}
"""

ARGUMENT_PARSER_PROMPT = """You are an expert argument analyst. Your task is to parse a debate argument into its structural components.

Given a user's argument, extract:
1. **main_claim**: The central assertion or thesis
2. **premises**: The explicit reasons given to support the claim
3. **implicit_assumptions**: Things the argument takes for granted without stating
4. **evidence_cited**: Any facts, data, statistics, or studies mentioned
5. **confidence_language**: Rate as "high", "medium", or "low" based on the language used:
   - "high" = uses words like "definitely", "obviously", "everyone knows", "clearly", "undeniably"
   - "medium" = uses moderate qualifiers like "I think", "it seems", "many people"
   - "low" = uses hedging like "might", "possibly", "I'm not sure but"

IMPORTANT RULES:
- If there are multiple distinct premises, list them separately — do NOT collapse them into one.
- Implicit assumptions are things NOT said but required for the argument to hold.
- If no evidence is cited, return an empty list for evidence_cited.
- Return ONLY valid JSON. No preamble, no explanation, no markdown formatting.

--- FEW-SHOT EXAMPLES ---

INPUT: "Social media should be banned for people under 16 because it causes depression in teenagers and kids can't handle it responsibly."

OUTPUT:
{
    "main_claim": "Social media should be banned for people under 16",
    "premises": [
        "Social media causes depression in teenagers",
        "Kids cannot handle social media responsibly"
    ],
    "implicit_assumptions": [
        "Depression in teenagers is primarily caused by social media rather than other factors",
        "A ban would be enforceable and effective",
        "There are no significant benefits of social media for teenagers that outweigh the harms"
    ],
    "evidence_cited": [],
    "confidence_language": "high"
}

INPUT: "I think universal basic income might actually work because Finland's pilot program showed that people didn't stop working and their mental health improved. Though I'm not sure it would scale to larger economies."

OUTPUT:
{
    "main_claim": "Universal basic income might actually work",
    "premises": [
        "Finland's UBI pilot program showed participants did not stop working",
        "The Finland pilot showed improvements in mental health"
    ],
    "implicit_assumptions": [
        "Results from Finland's small-scale pilot are relevant to other countries",
        "Mental health improvement and continued employment are sufficient indicators of UBI success"
    ],
    "evidence_cited": [
        "Finland's UBI pilot program results"
    ],
    "confidence_language": "low"
}

INPUT: "Climate change is clearly the biggest threat to humanity. The IPCC report shows temperatures will rise by 2 degrees by 2050. Every scientist agrees on this. We obviously need to switch to renewable energy immediately or we're doomed."

OUTPUT:
{
    "main_claim": "Climate change is the biggest threat to humanity and requires immediate switch to renewable energy",
    "premises": [
        "IPCC report predicts 2 degree temperature rise by 2050",
        "There is scientific consensus on climate change",
        "Failure to switch to renewable energy will lead to catastrophic outcomes"
    ],
    "implicit_assumptions": [
        "Climate change is a bigger threat than other existential risks like nuclear war or pandemics",
        "Switching to renewable energy is feasible on an immediate timeline",
        "Renewable energy alone is sufficient to address climate change"
    ],
    "evidence_cited": [
        "IPCC report on temperature projections"
    ],
    "confidence_language": "high"
}

INPUT: "Online education is arguably better than traditional classrooms. During COVID, a Stanford study found that students who used adaptive learning platforms scored 15% higher on standardized tests. Plus, it's more accessible for students in rural areas."

OUTPUT:
{
    "main_claim": "Online education is better than traditional classrooms",
    "premises": [
        "Students using adaptive learning platforms scored 15% higher on standardized tests during COVID",
        "Online education is more accessible for students in rural areas"
    ],
    "implicit_assumptions": [
        "Standardized test scores are a valid measure of educational quality",
        "COVID-era conditions are representative of normal online learning conditions",
        "Accessibility benefits outweigh potential drawbacks like reduced social interaction"
    ],
    "evidence_cited": [
        "Stanford study on adaptive learning platforms during COVID showing 15% improvement in test scores"
    ],
    "confidence_language": "medium"
}

INPUT: "Cryptocurrency is definitely the future of money because governments can't control it and it eliminates middlemen in transactions."

OUTPUT:
{
    "main_claim": "Cryptocurrency is the future of money",
    "premises": [
        "Governments cannot control cryptocurrency",
        "Cryptocurrency eliminates middlemen in transactions"
    ],
    "implicit_assumptions": [
        "Government control over currency is inherently bad",
        "Eliminating middlemen is always desirable in financial transactions",
        "Cryptocurrency's technical challenges (scalability, energy use) will be solved",
        "People will trust and adopt cryptocurrency widely enough to replace traditional money"
    ],
    "evidence_cited": [],
    "confidence_language": "high"
}

--- END EXAMPLES ---

Now parse the following argument:

INPUT: "{user_input}"

OUTPUT:
"""
