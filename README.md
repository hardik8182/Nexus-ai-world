# Nexus AI - Streamlit Deployment Guide (Hindi)

Yeh repo ek simple Streamlit app template rakhta hai jise aap Streamlit Cloud par deploy kar sakte hain.

Files:
- `nexus_ai.py` — main Streamlit app (use this as main file path on Streamlit Cloud)
- `requirements.txt` — dependencies

Quick steps (summary):

1) GitHub repo banayein
- Repository name: `nexus-ai-world`
- Public repo create karein
- Is repo me ye files commit/push karein

2) Streamlit Cloud par deploy karein
- Visit: https://share.streamlit.io
- Sign in with GitHub
- Click "New app" → "Use existing repo"
  - Repository: select `your-username/nexus-ai-world`
  - Main file path: `nexus_ai.py`
  - Branch: default (e.g., main)
- Click "Deploy"

3) Secrets setup (recommended; secure)
- Streamlit App page par "⋮" (App settings) → Settings → Secrets
- Wahan paste karein:
GROQ_API_KEY = "gsk_yaha_apni_lambi_si_key_paste_karein"
- Save karen

4) Local development (optional)
- Local testing ke liye create `.streamlit/secrets.toml` with:
  GROQ_API_KEY = "gsk_yaha_apni_lambi_si_key_paste_karein"
- Ya set environment variable: export GROQ_API_KEY="...."

5) Test automatic deployment
- Apne laptop par `nexus_ai.py` me koi chota change karein (e.g., title)
- Commit & push to GitHub
- Streamlit Cloud automatically detect karega aur redeploy karega

Notes:
- `nexus_ai.py` me maine ek generic REST request example diya hai. Groq ke exact request schema aur endpoint path ke liye aap Groq ki official docs dekh kar `url` aur `payload` adjust karen.
- Secrets kabhi code me hardcode na karein.
- Streamlit Cloud free tier per app ko thoda wake-up time lag sakta hai agar idle ho.
- GROQ API usage limits/billing check karen taaki aap unexpected charges se bach sakein.
