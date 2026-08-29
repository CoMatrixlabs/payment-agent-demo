"""The payments agent, as a LangGraph state machine.

Adapted from the LangGraph "customer support bot" tutorial pattern (MIT):
an assistant node bound to tools, a tool-executor node, and a human-approval interrupt
before any SENSITIVE (write/effectful) tool runs. The baseline exposes only read-only,
PII-free tools, so there is nothing to gate — the demo PR is what adds sensitive tools.

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
    "You are a payments help assistant. Help the customer with their own payments and "
    "questions only. Use search_help for how-to questions and payment_status to look up a "
    "payment's status. You have no access to customer records and cannot move money or send "
    "data anywhere."
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

    # HUMAN-IN-THE-LOOP: pause before executing any sensitive tool (none in the baseline).
    interrupt = ["tools"] if (settings.require_tool_approval and T.SENSITIVE_TOOLS) else []
    return g.compile(interrupt_before=interrupt)
