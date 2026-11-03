import streamlit as st
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

from agent.tokenwise_agent import agent
from utils.cost_tracker import tracker
from utils.config import settings
from tools.file_tools import WORKSPACE

st.set_page_config(
    page_title="TokenWise | Cost-Optimized Coding Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0f13 0%, #1a1a2e 100%); }
    .main-header {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #d946ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 700;
    }
    .metric-card {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #a5b4fc; }
    .metric-label { color: #64748b; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚡ TokenWise")
    st.markdown("---")
    
    st.markdown("### Model")
    model_options = {
        "Groq Llama 3.3 70B": "groq/llama-3.3-70b-versatile",
        "Groq Llama 3.1 8B": "groq/llama-3.1-8b-instant",
        "GPT-4o Mini": "gpt-4o-mini",
        "Local (Ollama)": "ollama/llama3.2",
    }
    selected_label = st.selectbox("Active Model", list(model_options.keys()))
    selected_model = model_options[selected_label]
    
    st.markdown("---")
    st.markdown("### Budget")
    new_budget = st.number_input("Daily Budget (USD)", min_value=0.1, max_value=50.0, value=float(tracker.daily_budget), step=0.5)
    if new_budget != tracker.daily_budget:
        tracker.daily_budget = new_budget
    
    summary = tracker.get_summary()
    st.metric("Today Spent", f"${summary['today_cost_usd']:.4f}")
    st.metric("Remaining", f"${summary['remaining_budget_usd']:.4f}")
    
    progress = min(summary['today_cost_usd'] / tracker.daily_budget, 1.0) if tracker.daily_budget > 0 else 0
    st.progress(progress)
    
    if summary['budget_exceeded']:
        st.error("Budget Exceeded")
    
    st.markdown("---")
    st.caption("TokenWise • Powered by Bifrost • Global AI Hackathon 2026")

# Main
st.markdown('<h1 class="main-header">TokenWise</h1>', unsafe_allow_html=True)
st.markdown("**Code smarter. Spend less.** Cost-optimized coding agent with Bifrost Gateway.")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">${summary["today_cost_usd"]:.4f}</div><div class="metric-label">TODAY COST</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["total_tokens"]:,}</div><div class="metric-label">TOTAL TOKENS</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{selected_label.split()[0]}</div><div class="metric-label">MODEL</div></div>', unsafe_allow_html=True)
with m4:
    status = "OK" if not summary["budget_exceeded"] else "Exceeded"
    color = "#6ee7b7" if not summary["budget_exceeded"] else "#fca5a5"
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{status}</div><div class="metric-label">BUDGET</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent_state = {
        "messages": [],
        "current_model": selected_model,
        "input_tokens": 0,
        "output_tokens": 0,
        "requires_approval": False,
        "pending_action": None,
        "status": "idle"
    }

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Describe the coding task..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if tracker.is_budget_exceeded():
        with st.chat_message("assistant"):
            st.error("Daily budget exceeded.")
        st.stop()
    
    with st.chat_message("assistant"):
        with st.spinner("TokenWise is working..."):
            try:
                st.session_state.agent_state["current_model"] = selected_model
                st.session_state.agent_state["messages"] = st.session_state.agent_state.get("messages", []) + [HumanMessage(content=prompt)]
                
                result = agent.invoke(st.session_state.agent_state)
                
                final_messages = result.get("messages", [])
                ai_response = ""
                for m in reversed(final_messages):
                    if isinstance(m, AIMessage) and m.content:
                        ai_response = m.content
                        break
                
                if not ai_response:
                    ai_response = "Task processed. Check the workspace for files."
                
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.agent_state = result
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.markdown("### Workspace")
if WORKSPACE.exists():
    files = [f for f in WORKSPACE.rglob("*") if f.is_file()]
    if files:
        for f in files[:15]:
            st.code(str(f.relative_to(WORKSPACE)))
    else:
        st.info("Workspace is empty. Ask TokenWise to create files.")
else:
    st.info("Workspace will appear after file operations.")
