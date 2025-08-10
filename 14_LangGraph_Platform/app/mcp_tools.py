"""Async MCP-backed tools for agent use.

Provides LangChain-compatible async tools that call a running MCP server via
FastMCP over streamable HTTP. Tools are added to the agent tool belt.
"""
from __future__ import annotations

import os
from typing import Any, Dict

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from langchain_core.tools import tool


def _get_mcp_server_url() -> str:
    """Return MCP server URL from env or default.

    Try root path first; callers can override to "/mcp" if server serves there.
    """
    return os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000")


async def _call_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Any:
    """Open a short-lived async MCP client and call a tool by name.

    Keeps implementation simple and robust. If performance becomes a concern,
    migrate to a shared, long-lived client with startup hooks.
    """
    base_url = _get_mcp_server_url()
    # Try base URL first, then "/mcp" fallback if server is mounted under a subpath
    candidate_urls = [base_url]
    if not base_url.rstrip("/").endswith("/mcp"):
        candidate_urls.append(base_url.rstrip("/") + "/mcp")

    last_exc: Exception | None = None
    for url in candidate_urls:
        try:
            transport = StreamableHttpTransport(url=url)
            client = Client(transport)
            async with client:
                return await client.call_tool(tool_name, params)
        except Exception as exc:  # try next candidate
            last_exc = exc
            continue
    # If all attempts failed, raise the last exception to surface a helpful error
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("MCP client failed without an exception; unexpected state")


@tool("check_stock_price")
async def mcp_check_stock_price(stock_symbol: str) -> str:
    """Get the current price of a stock symbol via MCP."""
    result = await _call_mcp_tool("check_stock_price", {"stock_symbol": stock_symbol})
    # Server returns a formatted string like "$123.45"; coerce to str to be safe
    return str(result)


@tool("get_comprehensive_stock_data")
async def mcp_get_comprehensive_stock_data(stock_symbol: str) -> str:
    """Get comprehensive stock data via MCP and stringify for the model."""
    result = await _call_mcp_tool(
        "get_comprehensive_stock_data", {"stock_symbol": stock_symbol}
    )
    return str(result)



