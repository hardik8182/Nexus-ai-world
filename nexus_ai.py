import streamlit as st
import requests
import json
import os

# Secrets fallback logic: Streamlit secrets -> local .streamlit/secrets.toml -> sidebar
if "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]
else:
    # local dev: allow .streamlit/secrets.toml or manual entry via sidebar
    groq_api_key = os.environ.get("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key", type="password")

st.title("Nexus AI: Worldwide Edition 🌍")

st.markdown(
    "Is demo me hum ek simple text prompt leke Groq (ya kisi bhi REST AI endpoint) ko request bhejenge. "
    "Apni actual Groq endpoint aur request body docs ke hisaab se URL/params update karein."
)

if not groq_api_key:
    st.warning(
        "Groq API key zaroori hai. Streamlit Cloud par `App Settings → Secrets` me `GROQ_API_KEY` add karein "
        "ya local testing ke liye `.streamlit/secrets.toml`/environment variable set karein."
    )
    st.stop()

prompt = st.text_area("Enter prompt", value="Write a friendly greeting in Hindi", height=150)

col1, col2 = st.columns([1, 1])
with col1:
    max_tokens = st.slider("Max tokens (example)", 50, 1000, 200)
with col2:
    temperature = st.slider("Temperature (example)", 0.0, 1.0, 0.2)

if st.button("Generate"):
    with st.spinner("Calling Groq (or your configured endpoint)..."):
        # TODO: Replace the URL and payload with the real Groq endpoint & expected JSON schema.
        url = "https://api.groq.com/v1/generate"  # <-- Replace with actual Groq endpoint
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Adjust extraction according to Groq's response schema
            output = None
            if isinstance(data, dict):
                if "output" in data:
                    output = data["output"]
                elif "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
                    ch = data["choices"][0]
                    output = ch.get("text") or ch.get("message") or ch
                else:
                    output = json.dumps(data, indent=2, ensure_ascii=False)
            else:
                output = str(data)

            st.subheader("Response")
            st.code(output, language="json")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
        except Exception as ex:
            st.error(f"Unexpected error: {ex}")
