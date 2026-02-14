"""
LangGraph workflow construction for agentic system
"""
import streamlit as st
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from code.core.state import AgentState
from code.nodes.planner import planner_node
from code.nodes.executor import executor_node
from code.nodes.evaluator import evaluator_node
from code.nodes.synthesizer import synthesizer_node


def route_after_evaluator(state: AgentState) -> str:
    """Route based on evaluator decision"""
    decision = state.get("evaluator_decision", "continue")

    if decision == "replan":
        return "planner"
    else:
        return "synthesizer"


@st.cache_resource
def build_agent():
    """Build the agentic workflow with loop logic"""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Define edges
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "evaluator")

    # Conditional edge from evaluator (loop or finish)
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            "planner": "planner",      # Loop back
            "synthesizer": "synthesizer"  # Finish
        }
    )

    workflow.add_edge("synthesizer", END)

    # Compile with checkpointer for conversation memory
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# Build agent instance
app = build_agent()
