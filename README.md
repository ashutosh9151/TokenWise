# ⚡ TokenWise

**Code smarter. Spend less.**

TokenWise is a cost-optimized AI coding agent that completes real development tasks while minimizing token usage and cost.

Built for the **Global AI Hackathon 2026** (Geek Room) with **Bifrost Gateway** integration.

## Features

- Bifrost Gateway integration (automatic failover)
- Real-time token & cost tracking
- Daily spending limits
- Model fallback support
- Local model support (Ollama)
- Human-in-the-loop for risky operations
- Clean modern UI
- Sandboxed workspace

## Quick Start

```bash
# 1. Start Bifrost
npx -y @maximhq/bifrost

# 2. Setup project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your `GROQ_API_KEY`.

```bash
streamlit run app.py
```

## Tech Stack

- LangGraph + LangChain
- Bifrost AI Gateway
- Streamlit
- Groq / OpenAI / Ollama

## Hackathon Alignment

This project addresses the Cost-Optimized Coding Agent challenge:
- Minimizes token consumption
- Handles provider outages via Bifrost
- Enforces spending limits
- Supports local models
- Safe file operations

---

MIT License © 2026 Ashutosh Prajapati
