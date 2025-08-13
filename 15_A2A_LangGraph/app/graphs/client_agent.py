from __future__ import annotations

import os
from typing import Annotated, Any, Dict, List, TypedDict
import json

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.tools import get_tool_belt
from app.a2a_agent_client import A2AAgentClient
from langchain_core.tools import BaseTool


class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


def _build_model_with_tools(model, tools):
    return model.bind_tools(tools)


def _call_model(state: Dict[str, Any], model, tools) -> Dict[str, Any]:
    model_with_tools = _build_model_with_tools(model, tools)
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def _route_action_or_end(state: Dict[str, Any]):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "action"
    return END


def build_graph():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Tool that constructs an A2A client on-demand inside each call
    class A2AOnDemandTool(BaseTool):
        name: str = "a2a_call"
        description: str = (
            "Call the external A2A agent to answer the user's question. "
            "Use this when you want the other agent to handle the query."
        )

        def _run(self, query: str) -> str:  # pragma: no cover
            raise NotImplementedError("Use the async version of this tool")

        async def _arun(self, query: str) -> str:
            base_url = os.getenv("A2A_BASE_URL", "http://localhost:10000")
            async with A2AAgentClient(base_url=base_url) as client:
                response: Dict[str, Any] = await client.send_text(query)
                return json.dumps(response)

    tools = get_tool_belt() + [A2AOnDemandTool()]

    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)

    def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
        return _call_model(state, model, tools)

    graph.add_node("agent", agent_node)
    graph.add_node("action", tool_node)
    graph.set_entry_point("agent")

    graph.add_conditional_edges("agent", _route_action_or_end, {"action": "action", END: END})
    graph.add_edge("action", "agent")

    return graph.compile()


# The CLI expects a module-level symbol named `graph`
graph = build_graph()


