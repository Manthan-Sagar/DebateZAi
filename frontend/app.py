"""
Streamlit Frontend — AI Debate Partner UI (Placeholder)
This will be built out in Week 3.

Run: streamlit run frontend/app.py
"""

import streamlit as st


def main():
    st.set_page_config(
        page_title="AI Debate Partner",
        page_icon="🎯",
        layout="wide",
    )

    st.title("🎯 AI Debate Partner & Concept Mastery Evaluator")
    st.markdown("---")
    st.info("🚧 **Frontend under construction.** Use `python main.py` for the CLI version.")
    st.markdown("""
    ### How it works:
    1. **Phase 1 — Debate Mode**: AI challenges your position
    2. **Phase 2 — Probe Mode**: AI tests your conceptual understanding
    3. **Phase 3 — Evaluation**: You receive a structured mastery report
    """)


if __name__ == "__main__":
    main()
