from __future__ import annotations

import asyncio
import json
from typing import Any
import os

from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import Field
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.a2a_agent_client import A2AAgentClient
from dotenv import load_dotenv


class A2ASendTextTool(BaseTool):
    """
    LangChain Tool that delegates a user query to the external A2A agent
    using the project's A2AAgentClient.
    """

    name: str = "a2a_call"
    description: str = (
        "Call the external A2A agent to answer the user's question. "
        "Use this when you want the other agent to handle the query."
    )
    client: A2AAgentClient = Field(..., description="Initialized A2A client instance")

    def _run(self, query: str) -> str:  # pragma: no cover - sync path unused in this project
        raise NotImplementedError("Use the async version of this tool")

    async def _arun(self, query: str) -> str:
        response: dict[str, Any] = await self.client.send_text(query)
        return json.dumps(response)


async def build_agent_with_client(client: A2AAgentClient):
    """
    Build a minimal ReAct-style agent (via LangGraph prebuilt) that can use the A2A tool.
    Returns a Runnable graph that accepts {"messages": [HumanMessage(...), ...]}.
    """
    # Load environment variables (e.g., from a .env file) so OPENAI_API_KEY is available
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")
    tool = A2ASendTextTool(client=client)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_react_agent(llm, [tool])
    return agent

graph = build_agent_with_client(A2AAgentClient(base_url="http://localhost:10000"))


async def demo() -> None:
    base_url = "http://localhost:10000"

    async with A2AAgentClient(base_url=base_url) as client:
        agent = await build_agent_with_client(client)

        # Single demonstration query
        result = await agent.ainvoke({
            "messages": [
                HumanMessage(content="Ask the external agent: what are the latest developments in AI?")
            ]
        })
        print(result)


if __name__ == "__main__":
    asyncio.run(demo())


