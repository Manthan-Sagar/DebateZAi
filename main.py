"""
AI Debate Partner & Concept Mastery Evaluator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Main session orchestrator — runs the 3-phase debate flow:
  Phase 1: Debate Mode (AI opposes, collects reasoning data)
  Phase 2: Probe Mode  (targeted questions, adaptive difficulty)
  Phase 3: Evaluation   (structured mastery report)

Usage:
    python main.py
"""

import json
import concurrent.futures
from config import DEBATE_TURNS
from modules.argument_parser import parse_argument
from modules.weakness_scorer import score_weaknesses, get_attack_strategy
from modules.fallacy_detector import detect_fallacies
from modules.rebuttal_generator import generate_rebuttal
from modules.adaptive_engine import AdaptiveEngine
from modules.consistency_tracker import ConsistencyTracker
from modules.stance_classifier import classify_stance
from modules.mastery_evaluator import MasteryEvaluator
from gemini_client import call_gemini_text
from modules.conclusion_detector import check_if_concluding


def get_ai_position(topic: str, user_position: str) -> str:
    """Generate the AI's opposing position on the topic."""
    prompt = f"""The user wants to debate the topic: "{topic}"
The user's position is: "{user_position}"

Generate a clear, concise opposing position that the AI will defend throughout the debate.
CRITICAL: Limit your response to 2 sentences maximum to keep the debate fast.
Return only the opposing position statement, nothing else."""

    return call_gemini_text(prompt)


def run_debate_session():
    """Run a full 3-phase debate session."""

    print("\n" + "━" * 60)
    print("  AI DEBATE PARTNER & CONCEPT MASTERY EVALUATOR")
    print("━" * 60 + "\n")

    # ── Setup ──
    topic = input("📋 Enter the debate topic: ").strip()
    user_position = input("🎯 Enter YOUR position on this topic: ").strip()

    print("\n⏳ Setting up the debate...")

    ai_position = get_ai_position(topic, user_position)
    print(f"\n🤖 AI's position: {ai_position}\n")

    # Initialize core modules
    adaptive_engine = AdaptiveEngine()
    consistency_tracker = ConsistencyTracker()

    # Generate concept graph for the topic
    print("📊 Building concept graph...\n")
    adaptive_engine.initialize_concept_graph(topic)

    conversation_history = []
    turn_number = 0
    all_fallacies = []

    # ════════════════════════════════════════════
    # MODE SELECTION
    # ════════════════════════════════════════════
    print("\n" + "=" * 50)
    print("  SELECT MODE")
    print("  1: Debate Mode (AI challenges your position)")
    print("  2: Knowledge Test Mode (AI probes your understanding)")
    print("=" * 50 + "\n")

    while True:
        mode_choice = input("Enter 1 or 2: ").strip()
        if mode_choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
        
    evaluator = MasteryEvaluator(topic, user_position, ai_position, mode=mode_choice)

    if mode_choice == '1':
        # ════════════════════════════════════════════
        # PHASE 1: DEBATE MODE
        # ════════════════════════════════════════════
        print("\n=" * 50)
        print("  PHASE 1: DEBATE MODE")
        print("  (AI will challenge your position)")
        print("=" * 50 + "\n")

        for i in range(DEBATE_TURNS):
            turn_number += 1

            # Get user input
            user_input = input(f"\n💬 [Turn {turn_number}] Your argument: ").strip()
            if not user_input:
                continue

            # ── Pipeline: Parse → Score → Detect → Classify → Rebuttal ──
            print("  🔍 Analyzing your argument...")

            # We can run independent tasks concurrently to save time
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 1 & 2. Task A: Parse and then score (sequential dependency)
                def parse_and_score(ui, t):
                    p = parse_argument(ui)
                    s = score_weaknesses(p, t)
                    return p, s
                
                future_parse_score = executor.submit(parse_and_score, user_input, topic)
                
                # 3. Task B: Detect fallacies
                future_fallacies = executor.submit(detect_fallacies, user_input, ai_position)
                
                # 4. Task C: Classify stance
                def get_stance(ui, ch):
                    if not ch:
                        return "new_argument"
                    return classify_stance(ui, ch)
                    
                future_stance = executor.submit(get_stance, user_input, conversation_history)
                
                # Task D: Check for early conclusion
                future_concluding = executor.submit(check_if_concluding, user_input)
                
                # Wait for all results to complete
                parsed, weakness_scores = future_parse_score.result()
                fallacies = future_fallacies.result()
                stance_type = future_stance.result()
                is_concluding = future_concluding.result()

            if is_concluding:
                print("\n🏁 I sense you are wrapping up the debate. Let's move on to your evaluation report!")
                # Record final turn before breaking
                conversation_history.append({"role": "user", "content": user_input})
                evaluator.record_turn(
                    turn_number, user_input, "User concluded the debate.",
                    parsed, weakness_scores, fallacies, stance_type
                )
                break

            all_fallacies.extend(fallacies.get("fallacies", []))

            # 5. Select attack strategy
            strategy = get_attack_strategy(
                weakness_scores.get("scored_premises", []),
                weakness_scores.get("most_vulnerable_premise_index", 0),
            )

            # 6. Check consistency
            consistency_tracker.record_user_position(
                parsed["main_claim"], parsed["premises"]
            )
            user_consistency = consistency_tracker.check_user_consistency({
                "claim": parsed["main_claim"],
                "premises": parsed["premises"],
            })

            # 7. Calculate Turn Objective and Generate summary
            if turn_number == 1:
                turn_objective = "Probe"
            elif turn_number < DEBATE_TURNS:
                turn_objective = "Weaken"
            else:
                turn_objective = "Trap"

            rebuttal = generate_rebuttal(
                topic=topic,
                ai_position=ai_position,
                parsed_argument=parsed,
                weakness_scores=weakness_scores,
                rebuttal_strategy=strategy,
                conversation_history=conversation_history,
                stance_type=stance_type,
                argument_type=weakness_scores.get("argument_type", "empirical"),
                turn_objective=turn_objective,
            )

            consistency_tracker.record_ai_position(rebuttal[:200])

            # ── Display ──
            if fallacies.get("fallacies"):
                for f in fallacies["fallacies"]:
                    score = f.get('confidence_score', 0.8)
                    cat = f.get('category', 'soft')
                    if cat == 'hard' or score >= 0.8:
                        print(f"  🚨 Logical Issue ({score}): {f.get('type', 'unknown').upper()} — {f.get('explanation', '')}")
                    else:
                        print(f"  💡 Possible Weakness ({score}): {f.get('type', 'unknown').upper()} — {f.get('explanation', '')} Want to examine this?")

            change_type = user_consistency.get("change_type", "consistent")
            if change_type == "contradiction":
                print(f"  🔄 Contradiction detected: {user_consistency.get('contradiction', '')}")
            elif change_type == "refinement":
                print(f"  📝 Argument refined: good evolution of your position.")

            print(f"\n🤖 [AI]: {rebuttal}\n")

            # ── Record ──
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "ai", "content": rebuttal})

            evaluator.record_turn(
                turn_number, user_input, rebuttal,
                parsed, weakness_scores, fallacies, stance_type
            )

    elif mode_choice == '2':
        # ════════════════════════════════════════════
        # PHASE 2: PROBE MODE
        # ════════════════════════════════════════════
        print("\n=" * 50)
        print("  PHASE 2: KNOWLEDGE TEST MODE")
        print("  (AI will test your understanding)")
        print("=" * 50 + "\n")

        print("Choose your confidence level for this topic:")
        print("  1: Beginner (3 Foundational Questions)")
        print("  2: Medium (6 Questions: 2 Foundational, 3 Intermediate, 1 Advanced)")
        print("  3: Advanced (10 Questions)")
        while True:
            conf_choice = input("Enter 1, 2, or 3: ").strip()
            if conf_choice in ['1', '2', '3']:
                break
            print("Invalid choice. Please enter 1, 2, or 3.")

        if conf_choice == '1':
            difficulty_sequence = ['foundational'] * 3
        elif conf_choice == '2':
            difficulty_sequence = ['foundational', 'foundational', 'intermediate', 'intermediate', 'intermediate', 'advanced']
        else:
            difficulty_sequence = ['foundational', 'foundational', 'intermediate', 'intermediate', 'intermediate', 'intermediate', 'advanced', 'advanced', 'advanced', 'advanced']

        for test_difficulty in difficulty_sequence:
            turn_number += 1

            # Generate probing question
            probe = adaptive_engine.generate_probing_question(
                topic, conversation_history, all_fallacies, target_difficulty=test_difficulty
            )

            question = probe.get("question", "Can you elaborate on your position?")
            print(f"\n🔬 [Probe {turn_number}] {question}")
            print(f"   (targeting: {probe.get('target_concept', 'general')}, "
                  f"difficulty: {test_difficulty})")

            # Get user response
            user_input = input(f"\n💬 Your answer: ").strip()
            if not user_input:
                continue

            is_concluding = check_if_concluding(user_input)
            if is_concluding:
                print("\n🏁 Ending the knowledge test early. Let's move on to your evaluation report!")
                conversation_history.append({"role": "user", "content": user_input})
                evaluator.record_turn(
                    turn_number, user_input, "User concluded the test.",
                    {"main_claim": "User Answer", "premises": [], "confidence_language": "medium", "evidence_cited": False}, 
                    {}, {"fallacies": []}, "probe_response"
                )
                break

            # Parse fallacies to keep track
            fallacies = detect_fallacies(user_input, ai_position)
            all_fallacies.extend(fallacies.get("fallacies", []))
            
            # Evaluate using structured grading prompt
            print("  🔍 Grading your answer...")
            try:
                evaluation = adaptive_engine.evaluate_answer(topic, question, user_input)
                score = float(evaluation.get("score", 5.0))
                what_was_good = evaluation.get("what_was_good", "Good attempt.")
                what_to_add = evaluation.get("what_to_add", "Consider expanding your points.")
            except Exception:
                score = 5.0
                what_was_good = "Could not parse evaluation."
                what_to_add = "Try to be more detailed."

            adaptive_engine.record_response_quality(score)

            # Display structured feedback
            print(f"\n✅ SCORE: {score}/10")
            print(f"👍 WHAT WAS GOOD: {what_was_good}")
            print(f"📈 WHAT TO ADD: {what_to_add}\n")

            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "ai", "content": f"Score: {score}/10\nGood: {what_was_good}\nAdd: {what_to_add}"})

            # Evaluator backwards compatibility requires parsed args, so we provide dummies for phase 2
            parsed_dummy = {"main_claim": "User Answer", "premises": [], "confidence_language": "medium", "evidence_cited": False}
            evaluator.record_turn(
                turn_number, user_input, f"Score: {score}/10\nGood: {what_was_good}\nAdd: {what_to_add}",
                parsed_dummy, {}, fallacies, "probe_response"
            )

    # ════════════════════════════════════════════
    # PHASE 3: EVALUATION MODE
    # ════════════════════════════════════════════
    print("\n=" * 50)
    print("  PHASE 3: EVALUATION")
    print("  (Generating your mastery report...)")
    print("=" * 50 + "\n")

    concept_summary = adaptive_engine.get_mastery_summary()
    report = evaluator.generate_report(concept_summary)

    print(report)
    print("\n" + "━" * 60)
    print("  Session complete. Thank you!")
    print("━" * 60 + "\n")


if __name__ == "__main__":
    run_debate_session()
