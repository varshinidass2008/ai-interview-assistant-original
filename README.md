# 🤖 AI Interview Assistant
**Practice smarter. Interview better.**

A Streamlit-based platform for personalized interview preparation — built as a PBL project for ECE placement training.

---

## ✨ Features
| Feature | Description |
|---|---|
| Role-specific questions | Embedded Engineer, Software Engineer, Electronics Engineer, General Placement |
| AI evaluation | Gemini → Groq → Ollama → Local Python fallback chain |
| Structured feedback | Strengths, weaknesses, missing points, model answer, recommendation |
| Priority engine | Ranks weak topics using performance, recency, importance, and mistake count |
| Streak tracker | Maintains daily practice streak |
| Interview history | Full record of every attempt, filterable by topic and score |

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Set AI API keys
```bash
export GEMINI_API_KEY="your_gemini_key"
export GROQ_API_KEY="your_groq_key"
```
You can also enter keys in the **Profile & Settings** page inside the app.

### 3. Run
```bash
streamlit run app.py
```
Then open **http://localhost:8501** in your browser.

---

## 🔐 Login
| Email | Password |
|---|---|
| demo@example.com | demo123 |

Or create a new account from the login screen.

---

## 📁 Project Structure
```
ai-interview-assistant/
├── app.py                    # Streamlit entry point
├── question_bank.py          # Structured question bank (50+ questions)
├── question_selector.py      # Ranked question selection
├── question_generator.py     # AI-assisted question generation
├── answer_evaluator.py       # AI + local evaluation & feedback
├── ai_provider.py            # Gemini / Groq / Ollama / local fallback
├── priority_engine.py        # Weak-topic priority scoring
├── streak_manager.py         # Daily practice streak
├── interview_history.py      # Record storage and retrieval
├── Components/
│   └── Navigation.py         # Sidebar navigation
├── pages/
│   ├── dashboard.py
│   ├── start_interview.py
│   ├── interview_history_page.py
│   └── profile_settings.py
├── utilities/
│   └── auth.py               # Login / account creation
├── data/                     # Auto-created: user history, streak, auth files
└── requirements.txt
```

---

## 🔄 AI Provider Fallback Chain
```
Gemini  →  Groq  →  Ollama (local)  →  Local Python Evaluator
```
The app **never crashes** due to a missing API key — the local evaluator always provides feedback.

---

## 📐 Priority Engine Formula
```
Priority(t) = w1×(1 − Performance(t))
            + w2×Importance(t)
            + w3×Mistakes(t)
            + w4×Recency(t)
            + w5×WeakHistory(t)

Weights: w1=0.35, w2=0.20, w3=0.20, w4=0.15, w5=0.10
```

---

*Built by Varshini Dass & Vijayasree M | Chennai Institute of Technology | ECE PBL 2026*
