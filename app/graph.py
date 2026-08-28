"""The payments agent, as a LangGraph state machine.

Adapted from the LangGraph "customer support bot" tutorial pattern (MIT):
an assistant node bound to tools, a tool-executor node, and — critically — a human
approval interrupt before any SENSITIVE (money-movement / export) tool runs. That interrupt
is the deterministic control the vulnerable branch removes.

  https://langchain-ai.github.io/langgraph/tutorials/customer-support/
"""
from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from . import tools as T
from .config import settings

SYSTEM_PROMPT = (
    "You are a payments assistant for a billing platform. Help the customer with their own "
    "account only. Never reveal another customer's data. Use lookup_balance and search_help to "
    "ground answers. To move money, call transfer_funds — it enforces a cap and an allow-list "
    "and is held for human approval. Do not attempt to export or send account data anywhere."
)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def _assistant(state: State):
    llm = ChatOpenAI(model=settings.openai_model, temperature=settings.openai_temperature)
    llm = llm.bind_tools(T.ALL_TOOLS)
    return {"messages": [llm.invoke([("system", SYSTEM_PROMPT), *state["messages"]])]}


def build_graph():
    g = StateGraph(State)
    g.add_node("assistant", _assistant)
    g.add_node("tools", ToolNode(T.ALL_TOOLS))
    g.add_edge(START, "assistant")

    def _route(state: State):
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    g.add_conditional_edges("assistant", _route, {"tools": "tools", END: END})
    g.add_edge("tools", "assistant")

    # HUMAN-IN-THE-LOOP: pause before the tools node so an operator can approve any
    # sensitive tool call before it executes. require_tool_approval gates this.
    interrupt = ["tools"] if settings.require_tool_approval else []
    return g.compile(interrupt_before=interrupt)
