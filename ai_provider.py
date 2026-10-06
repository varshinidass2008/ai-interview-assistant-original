"""
ai_provider.py
Abstraction layer: Gemini → Groq → Ollama → local Python evaluation.
All generation / evaluation calls pass through request_ai().
"""

import os
import json
import re

# ── PROVIDER ADAPTERS ─────────────────────────────────────────────────────────

def _call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
    except ImportError:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text


def _call_groq(prompt: str) -> str:
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return completion.choices[0].message.content


def _call_ollama(prompt: str) -> str:
    import requests
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "gemma:2b", "prompt": prompt, "stream": False},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("response", "")


# ── PROVIDER ORDER ────────────────────────────────────────────────────────────

_PROVIDERS = [
    ("Gemini", _call_gemini),
    ("Groq", _call_groq),
    ("Ollama", _call_ollama),
]


def request_ai(prompt: str) -> tuple[str, str]:
    """
    Try providers in order. Returns (result_text, provider_name).
    Raises RuntimeError only when ALL providers fail (caller uses local fallback).
    """
    errors = []
    for name, fn in _PROVIDERS:
        try:
            result = fn(prompt)
            if result and result.strip():
                return result.strip(), name
        except Exception as e:
            errors.append(f"{name}: {e}")
    raise RuntimeError("All AI providers failed: " + " | ".join(errors))


def get_provider_status() -> dict:
    """Return availability dict for UI display."""
    status = {}
    for name, fn in _PROVIDERS:
        try:
            _ = fn("Say OK in one word")
            status[name] = "✅ Available"
        except Exception as e:
            status[name] = f"❌ {str(e)[:60]}"
    status["Local Python"] = "✅ Always available"
    return status
