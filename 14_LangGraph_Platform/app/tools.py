"""Toolbelt assembly for agents.

Collects third-party tools and local tools (like RAG) into a single list that
graphs can bind to their language models.
"""
from __future__ import annotations

from typing import List

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from app.rag import retrieve_information
from app.mcp_tools import (
    mcp_check_stock_price,
    mcp_get_comprehensive_stock_data,
)
from app.mcp_dynamic_tools import get_discovered_mcp_tools


def get_tool_belt() -> List:
    """Return the list of tools available to agents (Tavily, Arxiv, RAG)."""
    tavily_tool = TavilySearchResults(max_results=5)
    toolbelt = [
        tavily_tool,
        ArxivQueryRun(),
        retrieve_information,
        # mcp_check_stock_price,
        # mcp_get_comprehensive_stock_data,
    ]
    # Append any dynamically discovered MCP tools (if available)
    try:
        toolbelt.extend(get_discovered_mcp_tools())
    except Exception:
        # Best-effort: if discovery fails, keep base tools
        pass
    return toolbelt


