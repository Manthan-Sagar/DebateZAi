# AI Debate Partner & Concept Mastery Evaluator — Implementation Plan

## Overview

Build an AI system that **debates you**, **evaluates your reasoning in real time**, **detects logical fallacies**, **adapts question difficulty to your performance**, and **produces a structured concept mastery report** at the end of each session.

**Three session phases:**
1. **Debate Mode** — AI takes an opposing position, collects data on your reasoning
2. **Probe Mode** — AI switches to targeted questions that expose conceptual gaps, difficulty adapts
3. **Evaluation Mode** — structured mastery report with scores, gaps, fallacies, and study recommendations

**Tech Stack:**
| Component | Tool | Why |
|---|---|---|
| Core LLM | Gemini 1.5 Flash API | Free tier, large context, fast |
| Classifier | DistilBERT (HuggingFace) | Lightweight, CPU-fast after quantization |
| Backend | Python | Clean, debuggable |
| State | Plain Python dicts | No overhead |
| Frontend (dev) | Streamlit | Working UI in ~50 lines |
| Visualization | vis.js | Live argument map |
| CMV data | PRAW | Reddit data collection |
| Training | HuggingFace Transformers + PyTorch | Industry standard |

---

## Proposed Changes

### 1. Project Scaffold

#### [NEW] [project root structure](file:///c:/Users/manth/Documents/AiDebaterSystem)

Create the full project directory tree:

```
AiDebaterSystem/
├── .env                          # GEMINI_API_KEY
├── .gitignore
├── requirements.txt
├── README.md
├── config.py                     # API config, model paths, constants
├── main.py                       # Session orchestrator (3-phase flow)
├── gemini_client.py              # Core Gemini API call wrapper
├── prompts/
│   ├── argument_parser.py        # Few-shot parser prompt
│   ├── weakness_scorer.py        # Vulnerability scoring prompt
│   ├── fallacy_detector.py       # Fallacy detection prompt
│   ├── rebuttal_generator.py     # Targeted rebuttal prompt
│   ├── adaptive_questions.py     # Probe question generation prompt
│   └── mastery_evaluator.py      # Session report prompt
├── modules/
│   ├── argument_parser.py        # Module 1: parse user input → structured JSON
│   ├── weakness_scorer.py        # Module 2: score premise vulnerability
│   ├── fallacy_detector.py       # Module 3: detect 6 fallacy types
│   ├── rebuttal_generator.py     # Rebuttal strategy selector + generator
│   ├── adaptive_engine.py        # Module 4: concept graph + question generation
│   ├── consistency_tracker.py    # Module 5: position memory + contradiction check
│   ├── stance_classifier.py      # Module 6: DistilBERT pushback classifier
│   └── mastery_evaluator.py      # Module 7: aggregation + report
├── models/
│   └── stance_model/             # Saved DistilBERT weights
├── data/
│   ├── cmv_labeled.csv           # Labeled CMV data (2-3k examples)
│   └── test_arguments.json       # 20+ test arguments for parser validation
├── training/
│   ├── collect_cmv_data.py       # PRAW script to pull CMV data
│   ├── label_cmv_data.py         # Weak supervision + manual labeling
│   ├── train_stance_model.py     # DistilBERT fine-tuning script
│   └── evaluate_model.py         # Accuracy, F1, confusion matrix
├── frontend/
│   └── app.py                    # Streamlit debate UI
└── tests/
    ├── test_parser.py            # Parser validation on 20 test arguments
    ├── test_scorer.py            # Weakness scorer tests
    ├── test_fallacy.py           # Fallacy over-detection tests
    └── test_consistency.py       # Contradiction detection tests
```

---

### 2. Gemini API Client (Day 1)

#### [NEW] [gemini_client.py](file:///c:/Users/manth/Documents/AiDebaterSystem/gemini_client.py)

- Core `call_gemini(prompt: str) -> dict` function used by every module
- Handles markdown code fence stripping from Gemini's JSON output
- Try/except with retry on JSON parse failures
- Loads API key from `.env`

---

### 3. Module 1 — Argument Parser (Days 1-2)

#### [NEW] [prompts/argument_parser.py](file:///c:/Users/manth/Documents/AiDebaterSystem/prompts/argument_parser.py)

**Prompt design with 5-6 few-shot examples.** Output schema:
```json
{
  "main_claim": "string",
  "premises": ["string", ...],
  "implicit_assumptions": ["string", ...],
  "evidence_cited": ["string", ...],
  "confidence_language": "high|medium|low"
}
```

#### [NEW] [modules/argument_parser.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/argument_parser.py)

- `parse_argument(raw_input: str) -> dict` — sends user text through parser prompt
- Validates JSON schema, retries on malformed output
- `confidence_language` detects overconfident language (definitely, obviously, everyone knows)

> [!IMPORTANT]
> **This is the single most critical module.** Spend ~30% of total effort getting the parser prompt right. If the parser is sloppy, every downstream module degrades. Target: clean JSON on 9/10 test inputs before moving on.

---

### 4. Module 2 — Weakness Scorer (Day 3)

#### [NEW] [modules/weakness_scorer.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/weakness_scorer.py)

Takes each premise from parser output and scores on 3 dimensions:
- **Evidence Score (0-1):** Unsupported assertion → 1.0 (maximally vulnerable)
- **Scope Score (0-1):** Overgeneralized claim → higher score
- **Causal Score (0-1):** Correlation-as-causation → 1.0

Premise with highest combined vulnerability score gets attacked first.

---

### 5. Module 3 — Fallacy Detector (Days 4-5)

#### [NEW] [modules/fallacy_detector.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/fallacy_detector.py)

Detects 6 fallacy types: Ad hominem, False dichotomy, Straw man, Hasty generalization, Appeal to authority, Circular reasoning.

Returns per-fallacy: name, triggering sentence, explanation.

> [!WARNING]
> **Over-detection risk.** Must include negative examples (clean arguments → zero fallacies) in the few-shot prompt. Test explicitly: a logically clean argument must return zero fallacies.

---

### 6. Rebuttal Generator (Days 6-7)

#### [NEW] [modules/rebuttal_generator.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/rebuttal_generator.py)

3 rebuttal strategies selected based on highest vulnerability dimension:
1. **Counterevidence** — "Studies show X contradicts your premise"
2. **Scope reduction** — "True in some cases, but your claim requires universality"
3. **Causal challenge** — "Even if A and B are true, you haven't shown A causes B"

---

### 7. Module 5 — Consistency Tracker (Week 2, Day 3)

#### [NEW] [modules/consistency_tracker.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/consistency_tracker.py)

- Python dict maintaining running log of all AI positions and all user positions
- Before each response, checks for contradictions with prior statements via Gemini
- Flags user self-contradictions (evaluation signal)
- No database required — in-memory dict passed as context to each Gemini call

---

### 8. Module 6 — Stance Firmness Classifier (Week 2, Days 1-5)

#### Data Collection & Training Pipeline

##### [NEW] [training/collect_cmv_data.py](file:///c:/Users/manth/Documents/AiDebaterSystem/training/collect_cmv_data.py)
- Pull comment threads from r/ChangeMyView using PRAW
- Use delta system as weak supervision signal for auto-labeling

##### [NEW] [training/train_stance_model.py](file:///c:/Users/manth/Documents/AiDebaterSystem/training/train_stance_model.py)
- Fine-tune `distilbert-base-uncased` with 4 labels: `new_argument`, `restatement`, `emotional_pressure`, `concession_with_reasoning`
- 3 epochs, batch size 16, warmup 200, weight_decay 0.01
- Save best model checkpoint

##### [NEW] [training/evaluate_model.py](file:///c:/Users/manth/Documents/AiDebaterSystem/training/evaluate_model.py)
- Overall accuracy target: 80%+
- Per-class F1 score (70%+ acceptable for `emotional_pressure`)
- Confusion matrix analysis
- INT8 quantization for fast CPU inference (<50ms)

##### [NEW] [modules/stance_classifier.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/stance_classifier.py)

- Loads quantized DistilBERT model
- `classify_stance(user_input: str) -> str` — returns one of 4 pushback types
- Determines AI response behavior:
  - `new_argument` → engage seriously, may adjust position
  - `restatement` → hold firm, acknowledge but don't concede
  - `emotional_pressure` → acknowledge feeling, maintain stance
  - `concession_with_reasoning` → high signal, score as strong reasoning

---

### 9. Module 4 — Adaptive Question Engine (Week 2, Days 6-7)

#### [NEW] [modules/adaptive_engine.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/adaptive_engine.py)

- Maintains a **concept graph** (Python dict or NetworkX) of the debate topic
- Tracks which concepts user has demonstrated understanding of vs. avoided
- Question generation logic:
  - Confident on X but never addressed Y (X depends on Y) → ask about Y
  - Claim requires knowing Z → probe Z specifically
  - Fallacy committed → probe whether intentional or misunderstanding
  - Strong response → harder question; Weak response → foundational question
- Gemini generates the topic concept graph at session start

---

### 10. Module 7 — Mastery Evaluator (Week 3, Days 1-2)

#### [NEW] [modules/mastery_evaluator.py](file:///c:/Users/manth/Documents/AiDebaterSystem/modules/mastery_evaluator.py)

Aggregates all turn data and produces structured report:
- **Overall score** (0-100)
- **Strengths** — citing specific turn numbers and claims
- **Gaps identified** — specific concepts avoided or weakly handled
- **Fallacies detected** — with turn numbers
- **Recommended study areas** — topical, not generic

> [!IMPORTANT]
> **Quality test:** Two users who argued differently on the same topic MUST get different reports. If reports feel generic or interchangeable, the evaluator prompt needs more specificity. Always pass the full structured session log, not just a summary.

---

### 11. Session Orchestrator

#### [NEW] [main.py](file:///c:/Users/manth/Documents/AiDebaterSystem/main.py)

Controls the 3-phase debate session:

1. **Phase 1 (Debate Mode):** User states position. AI debates for 6-8 turns using argument parser → weakness scorer → rebuttal generator pipeline. Collects reasoning quality data.
2. **Phase 2 (Probe Mode):** AI switches to targeted questions via adaptive engine. Difficulty adapts. 4-6 turns.
3. **Phase 3 (Evaluation Mode):** Mastery evaluator runs on full session data. Report displayed.

---

### 12. Streamlit Frontend (Week 3, Days 3-4)

#### [NEW] [frontend/app.py](file:///c:/Users/manth/Documents/AiDebaterSystem/frontend/app.py)

- Topic input and position selection
- Chat-style debate interface (left: user, right: AI)
- Phase indicator (Debate → Probe → Evaluate)
- Argument map visualization (vis.js embedded via `st.components.v1.html`)
- Mastery report display at session end

---

## User Review Required

> [!IMPORTANT]
> **LLM Choice:** The plan uses **Gemini 1.5 Flash** as specified in your roadmap. The free tier from Google AI Studio should be sufficient for development and demos.

> [!IMPORTANT]
> **Stance Classifier Training Data:** The DistilBERT fine-tuning requires ~2-3k labeled examples from Reddit CMV. You'll need a Reddit API client ID/secret (PRAW credentials) to collect data. If Reddit API access is difficult, we can use Gemini-based classification as a fallback (prompted, not fine-tuned) — less reliable but no training needed.

> [!IMPORTANT]
> **Build Order:** The plan follows the roadmap's recommended order — parser first, then scorer, then fallacy detector, then rebuttal generator. Each module is independently testable. The stance classifier training runs in parallel during Week 2.

---

## Verification Plan

### Automated Tests

Each module will have corresponding test files in `tests/`:

1. **Parser validation** — `python -m pytest tests/test_parser.py`
   - Run 20 manually crafted arguments through parser
   - Assert JSON schema compliance
   - Target: clean structured output on 18/20 (90%)

2. **Weakness scorer** — `python -m pytest tests/test_scorer.py`
   - Manually crafted arguments with known weakest premise
   - Assert scorer identifies the correct most-vulnerable premise
   - Target: 8/10 correct identification

3. **Fallacy detector** — `python -m pytest tests/test_fallacy.py`
   - Test clean, logically valid arguments → assert zero fallacies detected
   - Test known-fallacious arguments → assert correct fallacy type identified
   - Target: zero false positives on clean arguments

4. **Consistency tracker** — `python -m pytest tests/test_consistency.py`
   - Simulate a 10-turn debate with planted contradictions
   - Assert at least 3 contradictions are caught

5. **Stance classifier** — `python training/evaluate_model.py`
   - Evaluate on held-out test set
   - Print accuracy, per-class F1, confusion matrix
   - Target: 80%+ overall accuracy

6. **End-to-end debate loop** — `python -m pytest tests/test_e2e.py`
   - Full 14-turn session without errors
   - Each AI turn responds in under 5 seconds
   - Mastery report is generated with turn-specific citations

### Manual Verification

1. **Debate quality test (Week 1):**
   - Run `python main.py` and have a 5-turn debate on "Universal Basic Income"
   - Check: AI attacks the weakest premise, not random points
   - Check: Rebuttals feel targeted, not generic

2. **Stance firmness test (Week 2):**
   - Repeat the same argument back more forcefully 3 times
   - Check: AI holds firm and does not concede
   - Then introduce a genuinely new argument
   - Check: AI engages seriously with it

3. **Adaptive difficulty test (Week 2):**
   - Give strong, well-evidenced responses for 3 turns
   - Check: questions get harder (domain expert should find them challenging)
   - Give weak responses for 3 turns
   - Check: questions become more foundational

4. **Mastery report test (Week 3):**
   - Have two different people debate the same topic differently
   - Check: reports are meaningfully different, cite specific turns
   - Check: reports do NOT feel generic or interchangeable

5. **Frontend demo test (Week 3):**
   - Run `streamlit run frontend/app.py`
   - Complete a full 14-turn session through the UI
   - Check: no crashes, argument map updates correctly, report displays properly
