"""
answer_evaluator.py
Evaluates a student's typed answer and returns structured feedback.
Primary path: AI provider.  Final fallback: local keyword/concept matching.
"""

import json
import re
from ai_provider import request_ai

# ── KEYWORD BANKS FOR LOCAL FALLBACK ─────────────────────────────────────────

TOPIC_KEYWORDS = {
    "Embedded C / C++": [
        "pointer", "volatile", "static", "malloc", "calloc", "struct", "union",
        "bit field", "endian", "stack", "heap", "function pointer", "interrupt",
        "register", "extern", "typedef", "enum", "array", "memory", "null",
    ],
    "Microcontrollers": [
        "interrupt", "timer", "GPIO", "PWM", "ADC", "DAC", "SPI", "I2C",
        "UART", "watchdog", "ISR", "clock", "prescaler", "register",
        "microprocessor", "flash", "SRAM", "peripheral", "ARM", "cortex",
    ],
    "Communication Protocols": [
        "UART", "SPI", "I2C", "CAN", "baud", "clock", "master", "slave",
        "full duplex", "half duplex", "SDA", "SCL", "MISO", "MOSI",
        "acknowledge", "ACK", "NACK", "frame", "bit", "bus",
    ],
    "Digital Electronics": [
        "flip-flop", "latch", "gate", "combinational", "sequential",
        "Boolean", "Karnaugh", "multiplexer", "demultiplexer", "counter",
        "register", "adder", "encoder", "decoder", "truth table", "NAND", "NOR",
    ],
    "Debugging": [
        "oscilloscope", "logic analyzer", "breakpoint", "watchdog", "reset",
        "stack overflow", "fault", "trace", "assert", "JTAG", "SWD",
        "printf", "LED", "serial", "reproduce", "isolate",
    ],
    "Aptitude": [
        "speed", "time", "work", "probability", "ratio", "average",
        "percentage", "profit", "loss", "series", "algebra",
    ],
    "Project": [
        "design", "implement", "challenge", "solution", "technology",
        "contribute", "result", "test", "future", "improve",
    ],
    "Behavioral / HR": [
        "team", "communicate", "strength", "weakness", "goal", "conflict",
        "leadership", "challenge", "achieve", "responsible", "learn",
    ],
}


def _local_evaluate(
    question: str,
    answer: str,
    topic: str,
    difficulty: str,
) -> dict:
    """Rule-based evaluation when AI is unavailable."""
    answer_lower = answer.lower()
    keywords = TOPIC_KEYWORDS.get(topic, [])
    matched = [kw for kw in keywords if kw.lower() in answer_lower]
    missing = [kw for kw in keywords if kw.lower() not in answer_lower]

    word_count = len(answer.split())
    coverage = len(matched) / max(len(keywords), 1)

    if coverage >= 0.6 and word_count >= 40:
        evaluation = "Good answer with solid concept coverage."
        score_label = "Good"
    elif coverage >= 0.35 or word_count >= 20:
        evaluation = "Partial answer – some key concepts are present but others are missing."
        score_label = "Average"
    else:
        evaluation = "The answer is incomplete or lacks key technical terms."
        score_label = "Needs Improvement"

    strengths = f"Covered keywords: {', '.join(matched[:5]) if matched else 'None detected'}."
    weaknesses = f"Missing keywords: {', '.join(missing[:5]) if missing else 'None'}."
    missing_points = f"Consider addressing: {', '.join(missing[:6])}." if missing else "None identified."
    improved_answer = (
        f"A strong answer for '{topic}' should include: "
        f"{', '.join(keywords[:8])}. "
        f"Structure your answer clearly and provide an example where possible."
    )
    recommendation = f"Revise the '{topic}' section in your notes and practice explaining concepts aloud."

    return {
        "evaluation": evaluation,
        "score_label": score_label,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_points": missing_points,
        "improved_answer": improved_answer,
        "recommendation": recommendation,
        "provider": "Local Python Evaluator",
    }


def _parse_ai_response(text: str) -> dict:
    """Parse structured AI response. Handles both JSON and labeled text."""
    # Try JSON first
    try:
        data = json.loads(text)
        return {
            "evaluation": data.get("evaluation", ""),
            "score_label": data.get("score_label", "Evaluated"),
            "strengths": data.get("strengths", ""),
            "weaknesses": data.get("weaknesses", ""),
            "missing_points": data.get("missing_points", ""),
            "improved_answer": data.get("improved_answer", ""),
            "recommendation": data.get("recommendation", ""),
            "provider": data.get("provider", "AI"),
        }
    except Exception:
        pass

    # Fallback: extract labeled sections
    def extract(label):
        pattern = rf"{label}[:\-]\s*(.+?)(?=\n[A-Z]|\Z)"
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else ""

    return {
        "evaluation": extract("evaluation") or text[:300],
        "score_label": "Evaluated",
        "strengths": extract("strengths"),
        "weaknesses": extract("weaknesses"),
        "missing_points": extract("missing.?points"),
        "improved_answer": extract("improved.?answer"),
        "recommendation": extract("recommendation"),
        "provider": "AI",
    }


def evaluate_answer(
    role: str,
    round_type: str,
    topic: str,
    difficulty: str,
    question: str,
    answer: str,
) -> dict:
    """
    Main evaluation function.
    Returns a dict with keys:
      evaluation, score_label, strengths, weaknesses,
      missing_points, improved_answer, recommendation, provider
    """
    if not answer or not answer.strip():
        return {
            "evaluation": "No answer was provided.",
            "score_label": "Not Attempted",
            "strengths": "",
            "weaknesses": "Answer was empty.",
            "missing_points": "Everything.",
            "improved_answer": "",
            "recommendation": f"Attempt every question. Start with '{topic}' basics.",
            "provider": "System",
        }

    prompt = f"""You are an expert technical interviewer evaluating a student's answer.

Context:
- Role: {role}
- Interview Round: {round_type}
- Topic: {topic}
- Difficulty: {difficulty}

Question:
{question}

Student's Answer:
{answer}

Evaluate the answer against these criteria: relevance, correctness, technical concept coverage, completeness, and clarity.

Respond in this EXACT JSON format (no extra text):
{{
  "evaluation": "<2-3 sentence overall assessment>",
  "score_label": "<one of: Excellent / Good / Average / Needs Improvement>",
  "strengths": "<what the student did well>",
  "weaknesses": "<what is weak or incorrect>",
  "missing_points": "<key concepts that should have been covered>",
  "improved_answer": "<a well-structured model answer for this question>",
  "recommendation": "<specific topic or concept the student should revise next>"
}}"""

    try:
        text, provider = request_ai(prompt)
        result = _parse_ai_response(text)
        result["provider"] = provider
        return result
    except Exception:
        return _local_evaluate(question, answer, topic, difficulty)
