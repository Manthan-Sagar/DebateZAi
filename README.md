# 🎯 AI Debate Partner & Concept Mastery Evaluator

An advanced AI system that **debates you**, **evaluates your reasoning in real time**, **detects logical fallacies**, **adapts question difficulty to your performance**, and **produces a structured concept mastery report**. 

Designed to sharpen reasoning skills against a strategic AI adversary, it utilizes a combination of prompt engineering with large language models, a sophisticated Python-based logic engine, and a custom fine-tuned NLP classifier.

## 🛠️ Tech Stack & Libraries

This project leverages a diverse and powerful set of tools to enable real-time debate logic, fast NLP processing, and a beautiful UI:

### **Core LLM Backend**
- **Google Gemini (2.5 Flash):** The primary engine behind evaluating complex arguments via few-shot prompting.
- **Groq:** Lightning-fast API inferencing to keep the debate cadence real-time and snappy.
- **Ollama:** Facilitates completely local LLM execution, entirely bypassing API rate limits and ensuring complete privacy.

### **Machine Learning & NLP**
- **PyTorch & HuggingFace Transformers:** Built and executed the training pipeline for our custom **DistilBERT** stance classification model.
- **Scikit-learn:** Used for metric evaluation, classification reports, and handling severe dataset class imbalances via custom weighting.
- **Datasets (HuggingFace):** Handled large-scale synthetic dataset ingestion and processing.

### **Data & Logic Engines**
- **NetworkX:** Powers the **Adaptive Engine**, mapping complex conceptual relationships into topological graphs to dynamically track and probe the user's knowledge.
- **Pandas & NumPy:** Core utilities for tracking metrics, handling internal state, and matrix evaluations off-the-chain.
- **PRAW (Python Reddit API Wrapper):** Used for scraping massive amounts of real-world structured "Change My View" (CMV) arguments to fine-tune our classifiers.

### **Frontend & Architecture**
- **Streamlit:** Powers our heavily-customized, responsive 4-screen chat interface. We utilize its concurrent futures execution and session states heavily for real-time responsiveness.
- **Python-dotenv:** Securely manages environment variables across multiple dynamically-swapped LLM backends.

---

## ✨ Key Features

- **Interactive Debate Mode:** Engage in a back-and-forth debate where the AI challenges your position with dynamically generated counter-arguments and tracks your consistency.
- **Knowledge Test Mode (Probe Mode):** Test your understanding with adaptive probing questions that target specific gaps in your foundational, intermediate, and advanced knowledge.
- **Real-time Logic Evaluation:** Real-time flagging of "Hard" logical issues and "Soft" subjective weaknesses during the debate.
- **Comprehensive Mastery Report:** Get a detailed summary of your overarching argument structure, logical missteps, adaptability, and final mastery score.
- **Seamless Local/Cloud LLM Support:** Overcome API rate limits by seamlessly switching between Gemini (Cloud) and Ollama/Groq (Local) backends.

---

## 🏗️ System Architecture

The ecosystem runs in a smooth Multi-Phase Pipeline managed by a sleek Streamlit Frontend. 

### The 4 Application Screens
1. **Setup Screen:** Define the topic, your initial position, mode (Debate vs. Knowledge Test), and difficulty.
2. **Debate Mode:** Back-and-forth chat interface featuring inline fallacy badges and dynamic AI objectives (Probe ➝ Weaken ➝ Trap).
3. **Knowledge Test:** A focused QA mode that adaptively increases difficulty based on the quality of your responses.
4. **Evaluation Report:** Auto-generates a post-session mastery narrative summarizing strengths, fallacies, and areas for improvement.

### The 7 Core Engine Modules
| # | Module | Purpose | Approach |
|---|--------|---------|----------|
| 1 | **Argument Parser** | Extract claims, premises, and assumptions from raw user input. | LLM + Few-shot prompting |
| 2 | **Weakness Scorer** | Score each premise on evidence, scope, and causality. | LLM + Custom Rubric Evaluation |
| 3 | **Fallacy Detector** | Identify up to 6 distinct types of logical fallacies dynamically. | LLM + Few-shot (Anti-over-detection) |
| 4 | **Adaptive Engine** | Generate intelligent probing questions targeting specific knowledge gaps. | Python Concept Graph + LLM |
| 5 | **Consistency Tracker** | Track evolving positions and flag logical contradictions. | Python Dictionary States + LLM |
| 6 | **Stance Classifier** | Classify pushback types (new arg / restatement / emotional / concession). | **Fine-tuned DistilBERT** (Local Inference) |
| 7 | **Mastery Evaluator** | Generate structured end-of-session reports. | Python Aggregation + LLM Narrative |

---

## 🚀 Quick Start Guide

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/AiDebaterSystem.git
cd AiDebaterSystem
```

### 2. Set up Virtual Environment
```bash
python -m venv venv

# Activate Virtual Environment (Windows)
venv\Scripts\activate

# Activate Virtual Environment (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and configure your API keys or Local LLM Endpoints:
```bash
copy .env.example .env
# Edit .env and add your Gemini API Key from https://aistudio.google.com
```

If utilizing Local Models, ensure Ollama is running and your `config.py` is pointed towards the local server.

### 5. Launch the Application
```bash
streamlit run frontend/app.py
```

---

## 📁 Project Structure

```text
AiDebaterSystem/
├── config.py              # Central configuration & globals
├── gemini_client.py       # Core Gemini API/Local LLM wrapper
├── main.py                # Console-based Session orchestrator
├── frontend/              # Streamlit Web Application (app.py)
├── modules/               # The 7 core intelligence modules
│   ├── adaptive_engine.py
│   ├── argument_parser.py
│   ├── conclusion_detector.py
│   ├── consistency_tracker.py
│   ├── fallacy_detector.py
│   ├── mastery_evaluator.py
│   ├── rebuttal_generator.py
│   ├── stance_classifier.py
│   └── weakness_scorer.py
├── prompts/               # All LLM Prompt Templates
├── training/              # Optimization & DistilBERT Training Pipelines 
├── data/                  # Test data, labeled datasets, and CMV data
├── models/                # Saved local model weights (e.g. DistilBERT)
└── tests/                 # Unit tests & validation
```

---

## 🧠 Model Training & Fine-Tuning

A major component of the AI Debate Partner is its ability to structurally understand user text without solely relying upon external APIs. To achieve robust, low-latency execution, we fine-tuned a **DistilBERT** model to act as our **Stance Firmness Classifier**.

- Addressed severe class imbalances using weighted loss tracking and synthetic dataset generation.
- Implemented robust GPU-accelerated local pipeline using PyTorch and HuggingFace Transformers.
- Allows the system to near-instantly determine the fundamental stance of the user's incoming argument without costly API round-trips.

---

**Manthan | DTU Electrical Engineering**
