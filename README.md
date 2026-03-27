# AI Debate Partner & Concept Mastery Evaluator

An AI system that **debates you**, **evaluates your reasoning in real time**, **detects logical fallacies**, **adapts question difficulty to your performance**, and **produces a structured concept mastery report**.

> Built with Gemini 1.5 Flash + Fine-tuned DistilBERT | Python | Streamlit

## 🏗️ Architecture

The system runs in **3 phases** with **7 distinct modules**:

```
Phase 1: DEBATE MODE → AI challenges your position
Phase 2: PROBE MODE  → AI tests your understanding with targeted questions
Phase 3: EVALUATION   → Structured mastery report generated
```

### Modules
| # | Module | Purpose | Approach |
|---|--------|---------|----------|
| 1 | Argument Parser | Extract claims, premises, assumptions from input | Gemini + few-shot prompting |
| 2 | Weakness Scorer | Score each premise on evidence/scope/causality | Gemini + rubric prompt |
| 3 | Fallacy Detector | Identify 6 types of logical fallacies | Gemini + few-shot (with over-detection prevention) |
| 4 | Adaptive Question Engine | Generate probing questions targeting gaps | Concept graph (Python) + Gemini |
| 5 | Consistency Tracker | Track positions, flag contradictions | Python dict + Gemini check |
| 6 | Stance Firmness Classifier | Classify pushback type (new arg / restatement / emotional / concession) | Fine-tuned DistilBERT |
| 7 | Mastery Evaluator | Generate structured session report | Python aggregation + Gemini narrative |

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/AiDebaterSystem.git
cd AiDebaterSystem

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your Gemini API key
copy .env.example .env
# Edit .env and add your key from https://aistudio.google.com

# 5. Run the debate system
python main.py
```

## 📁 Project Structure

```
AiDebaterSystem/
├── config.py              # Central configuration
├── gemini_client.py       # Core Gemini API wrapper
├── main.py                # Session orchestrator (3-phase flow)
├── prompts/               # All Gemini prompt templates
├── modules/               # All 7 system modules
├── training/              # DistilBERT training pipeline
├── data/                  # Test data and labeled datasets
├── models/                # Saved model weights
├── frontend/              # Streamlit UI
└── tests/                 # Unit tests
```

## 🧠 Design Decisions

_TODO: Document key design decisions as you build._

## 🐛 What Went Wrong and How I Fixed It

_TODO: Document real engineering challenges and solutions._

---
**Manthan | DTU Electrical Engineering**
