"""
AI Debate Partner — Streamlit Frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chat-style web UI for the 3-phase debate flow.

Run:  streamlit run frontend/app.py
"""

import sys
import os

# Ensure project root is on the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
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
from modules.conclusion_detector import check_if_concluding
from gemini_client import call_gemini_text


# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Debate Partner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    .stApp { background-color: #0e1117; }

    /* Header */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2.2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .main-header p {
        color: #8b949e;
        font-size: 0.95rem;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        border-right: 1px solid #21262d;
    }

    /* Metric cards in sidebar */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card .label {
        color: #8b949e;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        color: #e6edf3;
        font-size: 1.25rem;
        font-weight: 600;
    }

    /* Fallacy badges */
    .fallacy-hard {
        background: rgba(248, 81, 73, 0.15);
        border: 1px solid rgba(248, 81, 73, 0.4);
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }
    .fallacy-soft {
        background: rgba(210, 153, 34, 0.15);
        border: 1px solid rgba(210, 153, 34, 0.4);
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }

    /* Report container */
    .report-container {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1rem;
    }

    /* Score display in knowledge test */
    .score-display {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: white;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Helper: AI Position Generator
# ──────────────────────────────────────────────
def get_ai_position(topic: str, user_position: str) -> str:
    prompt = f"""The user wants to debate the topic: "{topic}"
The user's position is: "{user_position}"

Generate a clear, concise opposing position that the AI will defend throughout the debate.
CRITICAL: Limit your response to 2 sentences maximum to keep the debate fast.
Return only the opposing position statement, nothing else."""
    return call_gemini_text(prompt)


# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
def init_session_state():
    defaults = {
        "screen": "setup",          # setup | debate | test | report
        "topic": "",
        "user_position": "",
        "ai_position": "",
        "mode": "1",                # 1=Debate, 2=Knowledge Test
        "confidence_level": "1",
        "conversation_history": [],
        "chat_messages": [],        # For display: [{role, content, meta}]
        "turn_number": 0,
        "all_fallacies": [],
        "adaptive_engine": None,
        "consistency_tracker": None,
        "evaluator": None,
        "difficulty_sequence": [],
        "difficulty_index": 0,
        "current_question": None,
        "report_text": "",
        "processing": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🎯 AI Debate Partner")
        st.markdown("---")

        if st.session_state.screen == "setup":
            st.markdown("*Configure your session below.*")
            return

        # Show session info
        st.markdown(f"""
<div class="metric-card">
    <div class="label">Topic</div>
    <div class="value" style="font-size: 0.95rem;">{st.session_state.topic}</div>
</div>
        """, unsafe_allow_html=True)

        mode_label = "⚔️ Debate Mode" if st.session_state.mode == "1" else "🔬 Knowledge Test"
        st.markdown(f"""
<div class="metric-card">
    <div class="label">Mode</div>
    <div class="value">{mode_label}</div>
</div>
        """, unsafe_allow_html=True)

        if st.session_state.screen == "debate":
            turn = st.session_state.turn_number
            max_turns = DEBATE_TURNS

            # Turn objective
            if turn <= 1:
                objective = "🔍 Probe"
            elif turn < max_turns:
                objective = "⚡ Weaken"
            else:
                objective = "🪤 Trap"

            st.markdown(f"""
<div class="metric-card">
    <div class="label">Turn</div>
    <div class="value">{turn} / {max_turns}</div>
</div>
<div class="metric-card">
    <div class="label">AI Objective</div>
    <div class="value">{objective}</div>
</div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🏁 End Debate", use_container_width=True, type="primary"):
                _generate_report()

        elif st.session_state.screen == "test":
            idx = st.session_state.difficulty_index
            total = len(st.session_state.difficulty_sequence)
            current_diff = st.session_state.difficulty_sequence[min(idx, total - 1)] if total > 0 else "N/A"

            st.markdown(f"""
<div class="metric-card">
    <div class="label">Question</div>
    <div class="value">{idx} / {total}</div>
</div>
<div class="metric-card">
    <div class="label">Difficulty</div>
    <div class="value">{current_diff.title()}</div>
</div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🏁 End Test", use_container_width=True, type="primary"):
                _generate_report()

        elif st.session_state.screen == "report":
            st.markdown("---")
            if st.button("🔄 New Session", use_container_width=True, type="primary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


# ──────────────────────────────────────────────
# Screen 1: Setup
# ──────────────────────────────────────────────
def render_setup():
    st.markdown("""
<div class="main-header">
    <h1>🎯 AI Debate Partner</h1>
    <p>Sharpen your reasoning against a strategic AI adversary</p>
</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### ⚙️ Session Setup")

        topic = st.text_input(
            "📋 Debate Topic",
            placeholder="e.g. Should AI be regulated by governments?",
            key="input_topic"
        )

        user_position = st.text_input(
            "🎯 Your Position",
            placeholder="e.g. Yes, AI needs strong government regulation",
            key="input_position"
        )

        st.markdown("---")

        mode = st.radio(
            "Select Mode",
            ["⚔️ Debate Mode — AI challenges your position",
             "🔬 Knowledge Test — AI probes your understanding"],
            key="input_mode"
        )

        confidence_level = "1"
        if "Knowledge Test" in mode:
            confidence_level = st.radio(
                "Confidence Level",
                ["1 — Beginner (3 questions)",
                 "2 — Medium (6 questions)",
                 "3 — Advanced (10 questions)"],
                key="input_confidence"
            )[0]

        st.markdown("")

        if st.button("🚀 Start Session", use_container_width=True, type="primary"):
            if not topic.strip() or not user_position.strip():
                st.error("Please fill in both the topic and your position.")
                return

            with st.spinner("⏳ Setting up the debate..."):
                mode_val = "1" if "Debate" in mode else "2"
                ai_pos = get_ai_position(topic.strip(), user_position.strip())

                # Initialize modules
                ae = AdaptiveEngine()
                ae.initialize_concept_graph(topic.strip())
                ct = ConsistencyTracker()
                ev = MasteryEvaluator(topic.strip(), user_position.strip(), ai_pos, mode=mode_val)

                # Build difficulty sequence for knowledge test
                diff_seq = []
                if mode_val == "2":
                    if confidence_level == "1":
                        diff_seq = ["foundational"] * 3
                    elif confidence_level == "2":
                        diff_seq = ["foundational", "foundational", "intermediate",
                                    "intermediate", "intermediate", "advanced"]
                    else:
                        diff_seq = ["foundational", "foundational",
                                    "intermediate", "intermediate", "intermediate", "intermediate",
                                    "advanced", "advanced", "advanced", "advanced"]

                # Save to session state
                st.session_state.topic = topic.strip()
                st.session_state.user_position = user_position.strip()
                st.session_state.ai_position = ai_pos
                st.session_state.mode = mode_val
                st.session_state.confidence_level = confidence_level
                st.session_state.adaptive_engine = ae
                st.session_state.consistency_tracker = ct
                st.session_state.evaluator = ev
                st.session_state.difficulty_sequence = diff_seq
                st.session_state.screen = "debate" if mode_val == "1" else "test"
                st.session_state.chat_messages = []
                st.session_state.conversation_history = []
                st.session_state.turn_number = 0
                st.session_state.all_fallacies = []
                st.session_state.difficulty_index = 0

                # For knowledge test, generate the first question
                if mode_val == "2":
                    _generate_next_question()

            st.rerun()


# ──────────────────────────────────────────────
# Screen 2: Debate Mode
# ──────────────────────────────────────────────
def render_debate():
    st.markdown(f"#### ⚔️ Debate: *{st.session_state.topic}*")
    st.info(f"🤖 **AI's Position:** {st.session_state.ai_position}")

    # Render chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

            # Show inline fallacy flags
            if msg.get("fallacies"):
                for f in msg["fallacies"]:
                    score = f.get("confidence_score", 0.8)
                    cat = f.get("category", "soft")
                    ftype = f.get("type", "unknown").upper()
                    explanation = f.get("explanation", "")
                    if cat == "hard" or score >= 0.8:
                        st.markdown(
                            f'<div class="fallacy-hard">🚨 <b>Logical Issue</b> ({score}): '
                            f'{ftype} — {explanation}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="fallacy-soft">💡 <b>Possible Weakness</b> ({score}): '
                            f'{ftype} — {explanation}. Want to examine this?</div>',
                            unsafe_allow_html=True
                        )

            # Show consistency info
            if msg.get("consistency"):
                change = msg["consistency"].get("change_type", "consistent")
                if change == "contradiction":
                    st.warning(f"🔄 Contradiction: {msg['consistency'].get('contradiction', '')}")
                elif change == "refinement":
                    st.success("📝 Argument refined: good evolution of your position.")

    # Check if debate is over
    if st.session_state.turn_number >= DEBATE_TURNS:
        st.markdown("---")
        st.info("🏁 Maximum turns reached! Generating your evaluation report...")
        _generate_report()
        st.rerun()
        return

    # Chat input
    user_input = st.chat_input("Type your argument...", key="debate_input")
    if user_input and not st.session_state.processing:
        st.session_state.processing = True
        _process_debate_turn(user_input)
        st.session_state.processing = False
        st.rerun()


def _process_debate_turn(user_input: str):
    """Run the full debate pipeline for a single turn."""
    ss = st.session_state
    ss.turn_number += 1
    turn = ss.turn_number

    # Run pipeline concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        def parse_and_score(ui, t):
            p = parse_argument(ui)
            s = score_weaknesses(p, t)
            return p, s

        future_ps = executor.submit(parse_and_score, user_input, ss.topic)
        future_f = executor.submit(detect_fallacies, user_input, ss.ai_position)
        future_st = executor.submit(
            lambda: classify_stance(user_input, ss.conversation_history) if ss.conversation_history else "new_argument"
        )
        future_c = executor.submit(check_if_concluding, user_input)

        parsed, weakness_scores = future_ps.result()
        fallacies = future_f.result()
        stance_type = future_st.result()
        is_concluding = future_c.result()

    # Early conclusion
    if is_concluding:
        ss.conversation_history.append({"role": "user", "content": user_input})
        ss.evaluator.record_turn(turn, user_input, "User concluded.", parsed, weakness_scores, fallacies, stance_type)
        ss.chat_messages.append({"role": "user", "content": user_input, "fallacies": [], "consistency": {}})
        _generate_report()
        return

    ss.all_fallacies.extend(fallacies.get("fallacies", []))

    # Attack strategy
    strategy = get_attack_strategy(
        weakness_scores.get("scored_premises", []),
        weakness_scores.get("most_vulnerable_premise_index", 0),
    )

    # Consistency
    ss.consistency_tracker.record_user_position(parsed["main_claim"], parsed["premises"])
    user_consistency = ss.consistency_tracker.check_user_consistency({
        "claim": parsed["main_claim"],
        "premises": parsed["premises"],
    })

    # Turn objective
    if turn == 1:
        turn_objective = "Probe"
    elif turn < DEBATE_TURNS:
        turn_objective = "Weaken"
    else:
        turn_objective = "Trap"

    # Generate rebuttal
    rebuttal_text = generate_rebuttal(
        topic=ss.topic,
        ai_position=ss.ai_position,
        parsed_argument=parsed,
        weakness_scores=weakness_scores,
        rebuttal_strategy=strategy,
        conversation_history=ss.conversation_history,
        stance_type=stance_type,
        argument_type=weakness_scores.get("argument_type", "empirical"),
        turn_objective=turn_objective,
    )

    ss.consistency_tracker.record_ai_position(rebuttal_text[:200])

    # Store display messages
    ss.chat_messages.append({
        "role": "user",
        "content": user_input,
        "fallacies": fallacies.get("fallacies", []),
        "consistency": user_consistency,
    })
    ss.chat_messages.append({
        "role": "assistant",
        "content": rebuttal_text,
    })

    # Store conversation history
    ss.conversation_history.append({"role": "user", "content": user_input})
    ss.conversation_history.append({"role": "ai", "content": rebuttal_text})

    # Record for evaluator
    ss.evaluator.record_turn(turn, user_input, rebuttal_text, parsed, weakness_scores, fallacies, stance_type)


# ──────────────────────────────────────────────
# Screen 3: Knowledge Test Mode
# ──────────────────────────────────────────────
def render_test():
    ss = st.session_state
    st.markdown(f"#### 🔬 Knowledge Test: *{ss.topic}*")

    # Render chat history
    for msg in ss.chat_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if msg.get("score_html"):
                st.markdown(msg["score_html"], unsafe_allow_html=True)

    # Check if all questions exhausted
    if ss.difficulty_index >= len(ss.difficulty_sequence):
        st.markdown("---")
        st.info("🏁 All questions answered! Generating your evaluation report...")
        _generate_report()
        st.rerun()
        return

    # Show current question if we have one and haven't displayed it yet
    if ss.current_question and not any(
        m.get("is_question_id") == ss.difficulty_index for m in ss.chat_messages
    ):
        q = ss.current_question
        question_text = q.get("question", "Can you elaborate?")
        difficulty = ss.difficulty_sequence[ss.difficulty_index]
        display_text = f"**[{difficulty.title()}]** {question_text}"
        ss.chat_messages.append({
            "role": "assistant",
            "content": display_text,
            "is_question_id": ss.difficulty_index,
        })
        st.rerun()

    # Chat input
    user_input = st.chat_input("Type your answer...", key="test_input")
    if user_input and not ss.processing:
        ss.processing = True
        _process_test_turn(user_input)
        ss.processing = False
        st.rerun()


def _process_test_turn(user_input: str):
    ss = st.session_state
    ss.turn_number += 1
    turn = ss.turn_number

    # Check for early conclusion
    is_concluding = check_if_concluding(user_input)
    if is_concluding:
        ss.conversation_history.append({"role": "user", "content": user_input})
        parsed_dummy = {"main_claim": "User Answer", "premises": [], "confidence_language": "medium", "evidence_cited": False}
        ss.evaluator.record_turn(turn, user_input, "User concluded.", parsed_dummy, {}, {"fallacies": []}, "probe_response")
        ss.chat_messages.append({"role": "user", "content": user_input})
        _generate_report()
        return

    # Add user message
    ss.chat_messages.append({"role": "user", "content": user_input})

    # Detect fallacies
    fallacies = detect_fallacies(user_input, ss.ai_position)
    ss.all_fallacies.extend(fallacies.get("fallacies", []))

    # Evaluate answer
    question = ss.current_question.get("question", "") if ss.current_question else ""
    try:
        evaluation = ss.adaptive_engine.evaluate_answer(ss.topic, question, user_input)
        score = float(evaluation.get("score", 5.0))
        what_was_good = evaluation.get("what_was_good", "Good attempt.")
        what_to_add = evaluation.get("what_to_add", "Consider expanding your points.")
    except Exception:
        score = 5.0
        what_was_good = "Could not parse evaluation."
        what_to_add = "Try to be more detailed."

    ss.adaptive_engine.record_response_quality(score)

    # Build feedback message
    feedback = f"**Score: {score}/10**\n\n👍 **What was good:** {what_was_good}\n\n📈 **What to add:** {what_to_add}"
    score_html = f'<div class="score-display">✅ Score: {score}/10</div>'
    ss.chat_messages.append({
        "role": "assistant",
        "content": feedback,
        "score_html": score_html,
    })

    # Update conversation history
    ss.conversation_history.append({"role": "user", "content": user_input})
    ss.conversation_history.append({"role": "ai", "content": f"Score: {score}/10\nGood: {what_was_good}\nAdd: {what_to_add}"})

    # Record for evaluator
    parsed_dummy = {"main_claim": "User Answer", "premises": [], "confidence_language": "medium", "evidence_cited": False}
    ss.evaluator.record_turn(
        turn, user_input,
        f"Score: {score}/10\nGood: {what_was_good}\nAdd: {what_to_add}",
        parsed_dummy, {}, fallacies, "probe_response"
    )

    # Move to next question
    ss.difficulty_index += 1
    if ss.difficulty_index < len(ss.difficulty_sequence):
        _generate_next_question()


def _generate_next_question():
    """Generate the next probing question."""
    ss = st.session_state
    idx = ss.difficulty_index
    if idx >= len(ss.difficulty_sequence):
        return

    difficulty = ss.difficulty_sequence[idx]
    ss.current_question = ss.adaptive_engine.generate_probing_question(
        ss.topic, ss.conversation_history, ss.all_fallacies,
        target_difficulty=difficulty
    )


# ──────────────────────────────────────────────
# Screen 4: Evaluation Report
# ──────────────────────────────────────────────
def render_report():
    st.markdown(f"#### 📊 Evaluation Report: *{st.session_state.topic}*")
    st.markdown("---")

    if not st.session_state.report_text:
        with st.spinner("🧠 Generating your mastery report... This may take a moment."):
            concept_summary = st.session_state.adaptive_engine.get_mastery_summary()
            report = st.session_state.evaluator.generate_report(concept_summary)
            st.session_state.report_text = report

    st.markdown(f"""
<div class="report-container">
{st.session_state.report_text}
</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Start New Session", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def _generate_report():
    """Transition to report screen."""
    st.session_state.screen = "report"


# ──────────────────────────────────────────────
# Main Router
# ──────────────────────────────────────────────
def main():
    render_sidebar()

    screen = st.session_state.screen
    if screen == "setup":
        render_setup()
    elif screen == "debate":
        render_debate()
    elif screen == "test":
        render_test()
    elif screen == "report":
        render_report()


if __name__ == "__main__":
    main()
