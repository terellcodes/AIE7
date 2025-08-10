"""Dynamic discovery of MCP tools exposed as LangChain tools.

This module queries a running MCP server for available tools and builds
LangChain StructuredTools on the fly using basic JSON Schema -> Pydantic
conversion. The discovered tools are cached for reuse.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List, Optional, Tuple, Type

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from pydantic import BaseModel, create_model
from langchain_core.tools import StructuredTool


def _mcp_urls() -> List[str]:
    base = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000")
    urls = [base]
    if not base.rstrip("/").endswith("/mcp"):
        urls.append(base.rstrip("/") + "/mcp")
    return urls


def _pytype_from_json_type(json_type: Optional[str]) -> Type[Any]:
    mapping: Dict[Optional[str], Type[Any]] = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        None: str,
    }
    return mapping.get(json_type, str)


def _args_model_from_schema(tool_name: str, schema: Dict[str, Any]) -> Type[BaseModel]:
    properties: Dict[str, Any] = schema.get("properties", {}) or {}
    required = set(schema.get("required", []) or [])
    fields: Dict[str, Tuple[Type[Any], Any]] = {}
    for field_name, spec in properties.items():
        py_type = _pytype_from_json_type(spec.get("type"))
        if field_name in required:
            fields[field_name] = (py_type, ...)
        else:
            fields[field_name] = (Optional[py_type], None)  # type: ignore[arg-type]
    if not fields:
        # No-arg tool still needs a schema model; include an optional placeholder
        fields["__dummy"] = (Optional[str], None)
    return create_model(f"{tool_name}Args", **fields)  # type: ignore[arg-type]


async def _call_mcp(tool_name: str, params: Dict[str, Any]) -> Any:
    last_exc: Exception | None = None
    for url in _mcp_urls():
        try:
            async with Client(StreamableHttpTransport(url=url)) as client:
                return await client.call_tool(tool_name, params)
        except Exception as exc:
            last_exc = exc
            continue
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("MCP call failed without an exception")


def _make_coroutine(tool_name: str):
    async def _coro(**kwargs):
        kwargs.pop("__dummy", None)
        return await _call_mcp(tool_name, kwargs)

    return _coro


async def discover_mcp_tools_async() -> List[StructuredTool]:
    tools: List[StructuredTool] = []
    last_exc: Exception | None = None
    for url in _mcp_urls():
        try:
            async with Client(StreamableHttpTransport(url=url)) as client:
                mcp_tools = await client.list_tools()
                for t in mcp_tools:
                    # Tools may be pydantic models (preferred) or plain dicts
                    if hasattr(t, "model_dump"):
                        data = t.model_dump()
                    elif isinstance(t, dict):
                        data = t
                    else:
                        # Fallback: best-effort attribute extraction
                        data = {
                            "name": getattr(t, "name", None),
                            "description": getattr(t, "description", ""),
                            "inputSchema": getattr(t, "input_schema", {}) or {},
                        }

                    name = data.get("name") or "mcp_tool"
                    description = data.get("description", "")
                    # Schema key may be camelCase in MCP objects
                    schema = data.get("inputSchema") or data.get("input_schema") or {}
                    ArgsModel = _args_model_from_schema(name, schema)
                    tools.append(
                        StructuredTool(
                            name=name,
                            description=description,
                            args_schema=ArgsModel,
                            coroutine=_make_coroutine(name),
                        )
                    )
                return tools
        except Exception as exc:
            last_exc = exc
            continue
    return tools


_CACHED_TOOLS: List[StructuredTool] | None = None


def get_discovered_mcp_tools() -> List[StructuredTool]:
    """Return cached MCP tools; discover once synchronously if needed.

    Uses asyncio.run for simplicity. If called from a running event loop,
    returns an empty list to avoid event loop conflicts.
    """
    global _CACHED_TOOLS
    if _CACHED_TOOLS is not None:
        return _CACHED_TOOLS

    try:
        _CACHED_TOOLS = asyncio.run(discover_mcp_tools_async())
    except RuntimeError:
        # Likely called from within a running loop; skip discovery here.
        _CACHED_TOOLS = []
    return _CACHED_TOOLS


def refresh_discovered_mcp_tools() -> None:
    """Clear cache; next call to get_discovered_mcp_tools will rediscover."""
    global _CACHED_TOOLS
    _CACHED_TOOLS = None


