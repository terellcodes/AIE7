import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from pprint import pprint
# Basic connection


async def run():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    # breakpoint()
    async with client:
        tools = await client.list_tools()
        pprint(f"Tools: {tools}")

        response = await client.call_tool("check_stock_price", {"stock_symbol": "AAPL"})
        pprint(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(run())