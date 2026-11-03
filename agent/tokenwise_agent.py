from typing import Annotated, TypedDict, Sequence, Optional, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from tools.file_tools import file_tools
from utils.cost_tracker import tracker
from utils.config import settings

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_model: str
    input_tokens: int
    output_tokens: int
    requires_approval: bool
    pending_action: Optional[str]
    status: str

def get_llm(model_name: str = None, temperature: float = 0.2):
    model_name = model_name or settings.default_model

    # Clean model name
    clean_name = model_name.replace("groq/", "").strip()

    # Bifrost path
    if settings.use_bifrost:
        return ChatOpenAI(
            model=model_name,
            api_key="not-needed",
            base_url=f"{settings.bifrost_base_url}/v1",
            temperature=temperature,
        )

    # Direct Groq
    try:
        if settings.groq_api_key:
            return ChatGroq(
                model=clean_name,
                api_key=settings.groq_api_key,
                temperature=temperature,
            )
        else:
            raise ValueError("GROQ_API_KEY not set in secrets")
    except Exception as e:
        print(f"⚠️ Model {clean_name} failed: {e}")
        # Final fallback
        if settings.groq_api_key:
            return ChatGroq(
                model="llama-3.1-8b-instant",
                api_key=settings.groq_api_key,
                temperature=temperature,
            )
        raise e

SYSTEM_PROMPT = """You are TokenWise — an intelligent, cost-optimized coding agent.

Your primary goals:
1. Complete the user's coding task correctly and efficiently.
2. Minimize token usage and cost at every step.
3. Be careful with file operations.

Rules:
- Always think step-by-step before acting.
- Prefer reading existing files before writing new ones.
- Keep responses concise.
- When you need to write or modify files, clearly state what you are about to do.
- You have access to tools: list_files, read_file, write_file, create_directory, delete_file.
- Never invent file contents. Always use tools.

Current workspace is sandboxed for safety.
"""

def call_model(state: AgentState):
    if tracker.is_budget_exceeded():
        return {
            "messages": [AIMessage(content="🛑 Daily budget exceeded. Please increase your budget or wait until tomorrow.")],
            "status": "budget_exceeded"
        }

    model_name = state.get("current_model") or settings.default_model
    llm = get_llm(model_name)
    llm_with_tools = llm.bind_tools(file_tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
    response = llm_with_tools.invoke(messages)

    input_text = " ".join([m.content for m in messages if hasattr(m, "content") and m.content])
    output_text = response.content or ""
    input_tokens = len(input_text) // 4
    output_tokens = len(output_text) // 4

    tracker.add_usage(
        model=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        task_preview=str(state["messages"][-1].content)[:60] if state["messages"] else ""
    )

    return {
        "messages": [response],
        "input_tokens": state.get("input_tokens", 0) + input_tokens,
        "output_tokens": state.get("output_tokens", 0) + output_tokens,
        "status": "running"
    }

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

def create_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(file_tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "agent")
    return workflow.compile()

agent = create_agent()
