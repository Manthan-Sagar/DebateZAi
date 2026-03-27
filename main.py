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
from config import DEBATE_TURNS, PROBE_TURNS
from modules.argument_parser import parse_argument
from modules.weakness_scorer import score_weaknesses, get_attack_strategy
from modules.fallacy_detector import detect_fallacies
from modules.rebuttal_generator import generate_rebuttal
from modules.adaptive_engine import AdaptiveEngine
from modules.consistency_tracker import ConsistencyTracker
from modules.stance_classifier import classify_stance
from modules.mastery_evaluator import MasteryEvaluator
from gemini_client import call_gemini_text


def get_ai_position(topic: str, user_position: str) -> str:
    """Generate the AI's opposing position on the topic."""
    prompt = f"""The user wants to debate the topic: "{topic}"
The user's position is: "{user_position}"

Generate a clear, concise opposing position that the AI will defend throughout the debate.
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

    # Initialize all modules
    adaptive_engine = AdaptiveEngine()
    consistency_tracker = ConsistencyTracker()
    evaluator = MasteryEvaluator(topic, user_position, ai_position)

    # Generate concept graph for the topic
    print("📊 Building concept graph...\n")
    adaptive_engine.initialize_concept_graph(topic)

    conversation_history = []
    turn_number = 0
    all_fallacies = []

    # ════════════════════════════════════════════
    # PHASE 1: DEBATE MODE
    # ════════════════════════════════════════════
    print("=" * 50)
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
            
            # Wait for all results to complete
            parsed, weakness_scores = future_parse_score.result()
            fallacies = future_fallacies.result()
            stance_type = future_stance.result()

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

        # 7. Generate rebuttal
        rebuttal = generate_rebuttal(
            topic=topic,
            ai_position=ai_position,
            parsed_argument=parsed,
            weakness_scores=weakness_scores,
            rebuttal_strategy=strategy,
            conversation_history=conversation_history,
            stance_type=stance_type,
        )

        consistency_tracker.record_ai_position(rebuttal[:200])

        # ── Display ──
        if fallacies.get("fallacies"):
            for f in fallacies["fallacies"]:
                print(f"  ⚠️  Fallacy detected: {f.get('type', 'unknown')} — {f.get('explanation', '')}")

        if not user_consistency.get("is_consistent", True):
            print(f"  🔄 Contradiction detected: {user_consistency.get('contradiction', '')}")

        print(f"\n🤖 [AI]: {rebuttal}\n")

        # ── Record ──
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "ai", "content": rebuttal})

        evaluator.record_turn(
            turn_number, user_input, rebuttal,
            parsed, weakness_scores, fallacies, stance_type
        )

    # ════════════════════════════════════════════
    # PHASE 2: PROBE MODE
    # ════════════════════════════════════════════
    print("\n" + "=" * 50)
    print("  PHASE 2: PROBE MODE")
    print("  (AI will test your understanding)")
    print("=" * 50 + "\n")

    for i in range(PROBE_TURNS):
        turn_number += 1

        # Generate probing question
        probe = adaptive_engine.generate_probing_question(
            topic, conversation_history, all_fallacies
        )

        question = probe.get("question", "Can you elaborate on your position?")
        print(f"\n🔬 [Probe {i+1}] {question}")
        print(f"   (targeting: {probe.get('target_concept', 'general')}, "
              f"difficulty: {probe.get('difficulty', 'intermediate')})")

        # Get user response
        user_input = input(f"\n💬 [Turn {turn_number}] Your answer: ").strip()
        if not user_input:
            continue

        # Parse and evaluate response
        parsed = parse_argument(user_input)
        fallacies = detect_fallacies(user_input, ai_position)
        all_fallacies.extend(fallacies.get("fallacies", []))
        weakness_scores = score_weaknesses(parsed, topic)

        # Score the response quality (simple heuristic for now)
        quality_score = 0.5
        if parsed.get("evidence_cited"):
            quality_score += 0.2
        if parsed.get("confidence_language") == "low":
            quality_score -= 0.1
        if not fallacies.get("fallacies"):
            quality_score += 0.1
        adaptive_engine.record_response_quality(min(1.0, max(0.0, quality_score)))

        # AI feedback on the answer
        feedback_prompt = f"""The user was asked this probing question about {topic}:
"{question}"

They answered: "{user_input}"

Give a brief (2-3 sentence) evaluation of their answer. Point out what was strong and what was missing. Be specific."""

        feedback = call_gemini_text(feedback_prompt)
        print(f"\n🤖 [AI]: {feedback}\n")

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "ai", "content": feedback})

        evaluator.record_turn(
            turn_number, user_input, feedback,
            parsed, weakness_scores, fallacies, "probe_response"
        )

    # ════════════════════════════════════════════
    # PHASE 3: EVALUATION MODE
    # ════════════════════════════════════════════
    print("\n" + "=" * 50)
    print("  PHASE 3: EVALUATION")
    print("  (Generating your mastery report...)")
    print("=" * 50 + "\n")

    concept_summary = adaptive_engine.get_mastery_summary()
    report = evaluator.generate_report(concept_summary)

    print(report)
    print("\n" + "━" * 60)
    print("  Session complete. Thank you for debating!")
    print("━" * 60 + "\n")


if __name__ == "__main__":
    run_debate_session()
