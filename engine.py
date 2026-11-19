import os
from typing import TypedDict, List
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# 2. State Schema
class AgentState(TypedDict):
    task_goal: str
    user_attempt: str
    hint_level: int
    is_solved: bool
    responses: List[str]
    tool_log: List[str]

# 3. Structured Evaluation Schema
class EvaluationOutput(BaseModel):
    is_solved: bool = Field(description="Whether the user's input successfully solves or completes the pattern/sequence challenge.")
    reasoning: str = Field(description="Step-by-step logic checking if the user's attempt matches the sequence pattern or task goal.")
    feedback: str = Field(description="Immersive narrative response providing direct feedback on the user's attempt.")
    suggested_hint_level: int = Field(description="Updated hint level based on attempt progress.")

# Models
evaluator_llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.7, timeout=30, max_retries=1)
structured_evaluator = evaluator_llm.with_structured_output(EvaluationOutput)

hint_llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.5, timeout=30, max_retries=1)

# Helper: pull plain text out of a model response (content can be a string or a list of blocks)
def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif isinstance(block, str):
            parts.append(block)
    return "".join(parts).strip()

# Node 1: Evaluator Node
async def evaluator_node(state: AgentState) -> dict:
    system_instruction = (
        "You are the evaluator for a puzzle game engine for kids aged 8-10. "
        "Analyze the user's attempt against the task goal. "
        "Determine if the user correctly identified, continued, or solved the sequence or puzzle pattern. "
        "If they are correct, set is_solved to True and provide congratulatory narrative feedback. "
        "If they are incorrect, set is_solved to False and provide helpful feedback without revealing the full answer immediately."
    )
    prompt = (
        f"{system_instruction}\n\n"
        f"Task Goal: {state['task_goal']}\n"
        f"User Attempt: {state['user_attempt']}\n"
        f"Current Hint Level: {state['hint_level']}"
    )
    result = await structured_evaluator.ainvoke(prompt)
    return {
        "is_solved": result.is_solved,
        "responses": state.get("responses", []) + [result.feedback],
        "hint_level": result.suggested_hint_level,
        "tool_log": state.get("tool_log", []) + [f"Eval::is_solved={result.is_solved}"],
    }

# Conditional Routing Edge
def route_next_step(state: AgentState) -> str:
    if state["is_solved"]:
        return END
    if state["hint_level"] >= 3:
        return END
    return "hint_escalator"

# Node 2: Hint Escalator Node (LLM-generated)
async def hint_node(state: AgentState) -> dict:
    # Use the level the evaluator set, but never below 1 for the first hint
    new_level = max(state.get("hint_level", 0), 1)
    prompt = (
        "You are giving a hint for a pattern puzzle for kids aged 8-10. "
        f"Task: {state['task_goal']}\n"
        f"Learner's last attempt: {state['user_attempt']}\n"
        f"Hint level: {new_level} (1 = gentle nudge, 3 = very specific). "
        "Give one hint at this level. Never state the final answer."
    )
    result = await hint_llm.ainvoke(prompt)
    hint_text = extract_text(result.content)
    return {
        "responses": state.get("responses", []) + [hint_text],
        "hint_level": new_level,
        "tool_log": state.get("tool_log", []) + [f"Hint::Level_{new_level}"],
    }

# Build StateGraph
builder = StateGraph(AgentState)
builder.add_node("evaluator", evaluator_node)
builder.add_node("hint_escalator", hint_node)

builder.set_entry_point("evaluator")
builder.add_conditional_edges(
    "evaluator",
    route_next_step,
    {END: END, "hint_escalator": "hint_escalator"},
)
builder.add_edge("hint_escalator", END)

agent_graph = builder.compile()