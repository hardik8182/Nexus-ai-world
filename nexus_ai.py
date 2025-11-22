import streamlit as st
import requests
import json
import os
import time
from typing import Any, Dict, Optional

# Configuration - can be overridden via Streamlit secrets or environment
GROQ_API_URL = st.secrets.get("GROQ_API_URL", os.environ.get("GROQ_API_URL", "https://api.groq.com/v1/generate"))
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

# App title
st.set_page_config(page_title="Nexus AI", page_icon="🌍")
st.title("Nexus AI: Worldwide Edition 🌍")

st.markdown(
    """
    A lightweight Streamlit front-end that demonstrates calling an LLM-style REST API (Groq or similar).

    Features added:
    - Secrets-first approach (Streamlit secrets -> env var -> sidebar fallback)
    - Prompt templates
    - Per-session usage counter and basic rate-limit warning
    - Simple retry logic with exponential backoff
    - Configurable API URL via secrets (GROQ_API_URL)
    """
)

# Secrets / Key handling
if not GROQ_API_KEY:
    GROQ_API_KEY = st.sidebar.text_input("Groq API Key", type="password")

if not GROQ_API_KEY:
    st.warning("Groq API key required. Add `GROQ_API_KEY` in Streamlit Secrets or paste in the sidebar for local testing.")
    st.stop()

# Session usage counter
if "requests_made" not in st.session_state:
    st.session_state.requests_made = 0

RATE_LIMIT_WARN = 10  # warn after this many requests per session

# Prompt templates
TEMPLATES = {
    "Friendly Hindi greeting": "Write a friendly, short greeting in Hindi for a new user.",
    "Explain like I'm 5": "Explain the concept in simple terms and give an example.",
    "Summarize": "Summarize the following text in 2-3 sentences:",
}

template_name = st.selectbox("Prompt template", ["(custom)"] + list(TEMPLATES.keys()))
if template_name != "(custom)":
    prompt = st.text_area("Prompt", value=TEMPLATES[template_name], height=150)
else:
    prompt = st.text_area("Prompt", value="Write a friendly greeting in Hindi", height=150)

col1, col2 = st.columns([1, 1])
with col1:
    max_tokens = st.slider("Max tokens (example)", 50, 1000, 200)
with col2:
    temperature = st.slider("Temperature (example)", 0.0, 1.0, 0.2)

# Helper: robust POST with retries
def post_with_retries(url: str, headers: Dict[str, str], payload: Dict[str, Any], retries: int = 3, backoff: float = 1.0) -> Optional[Dict[str, Any]]:
    attempt = 0
    while attempt <= retries:
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt > retries:
                raise
            sleep_time = backoff * (2 ** (attempt - 1))
            time.sleep(sleep_time)

# Generic response extractor
def extract_text_from_response(data: Any) -> str:
    """Try a few common response shapes (Groq, OpenAI, Anthropic-style)."""
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        # Groq-style: maybe 'output'
        if "output" in data:
            return json.dumps(data["output"], ensure_ascii=False, indent=2) if not isinstance(data["output"], str) else data["output"]
        # OpenAI/choices style
        if "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
            first = data["choices"][0]
            if isinstance(first, dict):
                return first.get("text") or first.get("message") or json.dumps(first, ensure_ascii=False)
            return str(first)
        # common direct fields
        for key in ("text", "message", "result"):
            if key in data:
                return data[key]
        # fallback to pretty JSON
        return json.dumps(data, ensure_ascii=False, indent=2)
    # other types (list etc.)
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return str(data)

st.markdown(f"**Session requests made:** {st.session_state.requests_made}")
if st.session_state.requests_made >= RATE_LIMIT_WARN:
    st.warning(f"You have made {st.session_state.requests_made} requests this session. Consider limiting usage to avoid hitting API limits.")

if st.button("Generate"):
    with st.spinner("Calling API..."):
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            data = post_with_retries(GROQ_API_URL, headers, payload, retries=3, backoff=1.0)
            output = extract_text_from_response(data)
            st.subheader("Response")
            st.code(output, language="json")

            # update usage counter
            st.session_state.requests_made += 1
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
        except Exception as ex:
            st.error(f"Unexpected error: {ex}")