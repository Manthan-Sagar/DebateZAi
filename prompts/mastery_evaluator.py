"""
Phase 3 Prompts — Formatting the final reports depending on the chosen mode.
"""

DEBATE_REPORT_PROMPT = """You are an expert debate coach evaluating a user's performance in a Debate on the topic: "{topic}".
The user's stance was: "{user_position}".
The AI's stance was: "{ai_position}".

Here is a human-readable summary of the entire debate:
{clean_session_log}

Here is a summary of the logical fallacies the user committed (if any):
{fallacy_summary}

Based on the debate log, generate a comprehensive "Debate Evaluation Report" formatted in Markdown.
Your report MUST include the following sections:

1. **Overall Performance**: A brief summary of how well they defended their stance.
2. **Arguments Left Behind**: What strong arguments for "{user_position}" did the user fail to mention?
3. **Line-by-Line Fallacy Breakdown**: Discuss the specific fallacies they committed, why they were fallacious, and how they harmed their argument.
4. **Presentation & Framing Strategy**: How could the user have framed their arguments more effectively or persuasively?
5. **Advanced Tactic - Trapping the Opponent**: Provide a specific, logical debate "trap" the user could have used against the AI's stance ("{ai_position}") to corner it.

Output the final report directly. Do not include any JSON or preamble.
"""

TEST_REPORT_PROMPT = """You are an expert educator evaluating a user's performance on a Knowledge Test regarding the topic: "{topic}".

Here is a human-readable summary of the test questions, the user's answers, and their scores:
{clean_session_log}

Based on the test log, generate a comprehensive "Knowledge Mastery Report" formatted in Markdown.
Your report MUST include the following sections:

1. **Cumulative Grade**: Calculate their overall performance out of 100 based on the scores provided.
2. **Overall Knowledge Assessment**: A brief summary of their current level of understanding of "{topic}".
3. **Point-by-Point Analysis**: For EVERY question asked, provide:
   - The user's score.
   - What they correctly understood.
   - The EXACT missing knowledge they needed to score a perfect 10/10. Teach them this concept clearly.
4. **Study Recommendations**: 2-3 specific sub-topics they should focus on studying to master this subject.

Output the final report directly. Do not include any JSON or preamble.
"""
