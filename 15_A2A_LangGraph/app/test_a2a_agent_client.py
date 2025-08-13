import asyncio
from typing import Any
import logging
from app.a2a_agent_client import A2AAgentClient


async def main() -> None:
    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance
    base_url = "http://localhost:10000"

    # Use context manager so the underlying httpx client is cleaned up automatically
    async with A2AAgentClient(base_url=base_url) as client:
        # Single-turn
        single_resp: dict[str, Any] = await client.send_text(
            "What are the latest developments in artificial intelligence?"
        )
        print({"single_turn": single_resp})

        # Multi-turn (start)
        start_resp, task_id, context_id = await client.start_task(
            "Find me recent papers on transformer architectures"
        )
        print({"multi_turn_start": start_resp, "task_id": task_id, "context_id": context_id})

        # Multi-turn (continue)
        continue_resp = await client.continue_task(
            "Can you summarize the key findings?", task_id=task_id, context_id=context_id
        )
        print({"multi_turn_continue": continue_resp})

        # Streaming (prints chunks as they arrive)
        async for chunk in client.stream_text(
            "Give me a brief overview of diffusion models"
        ):
            print({"stream_chunk": chunk})


if __name__ == "__main__":
    asyncio.run(main())


