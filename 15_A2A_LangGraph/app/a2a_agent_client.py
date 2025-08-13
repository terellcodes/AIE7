from __future__ import annotations

from typing import Any, AsyncIterator
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest, SendStreamingMessageRequest
from a2a.utils.constants import EXTENDED_AGENT_CARD_PATH


class A2AAgentClient:
    """
    High-level async client that encapsulates core A2A interactions used in this project.

    Responsibilities:
    - Resolve and select the effective AgentCard (public by default; authenticated extended when available and authorized)
    - Provide single-turn, multi-turn, and streaming message APIs
    - Manage the lifecycle of an internal httpx.AsyncClient when not provided by the caller
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 60.0,
        auth_token: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._auth_token = auth_token
        self._external_httpx_client = httpx_client

        self._httpx_client: httpx.AsyncClient | None = None
        self._owns_httpx_client: bool = False
        self._resolver: A2ACardResolver | None = None
        self._agent_card: AgentCard | None = None
        self._client: A2AClient | None = None

    @classmethod
    async def create(
        cls,
        base_url: str,
        *,
        timeout_seconds: float = 60.0,
        auth_token: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> "A2AAgentClient":
        """
        Async factory that returns an initialized instance ready for use.
        """
        self = cls(
            base_url,
            timeout_seconds=timeout_seconds,
            auth_token=auth_token,
            httpx_client=httpx_client,
        )
        await self._initialize()
        return self

    async def _initialize(self) -> None:
        if self._external_httpx_client is not None:
            self._httpx_client = self._external_httpx_client
            self._owns_httpx_client = False
        else:
            self._httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(self._timeout_seconds))
            self._owns_httpx_client = True

        assert self._httpx_client is not None

        self._resolver = A2ACardResolver(
            httpx_client=self._httpx_client,
            base_url=self._base_url,
        )

        self._agent_card = await self._fetch_effective_agent_card()
        self._client = A2AClient(httpx_client=self._httpx_client, agent_card=self._agent_card)

    async def _fetch_effective_agent_card(self) -> AgentCard:
        assert self._resolver is not None
        # Fetch public agent card first
        public_card = await self._resolver.get_agent_card()

        use_extended = bool(public_card.supports_authenticated_extended_card) and bool(self._auth_token)
        if not use_extended:
            return public_card

        # Attempt to fetch authenticated extended card; fall back to public on failure
        try:
            headers = {"Authorization": f"Bearer {self._auth_token}"}
            extended_card = await self._resolver.get_agent_card(
                relative_card_path=EXTENDED_AGENT_CARD_PATH,
                http_kwargs={"headers": headers},
            )
            return extended_card
        except Exception:
            return public_card

    @property
    def agent_card(self) -> AgentCard:
        if self._agent_card is None:
            raise RuntimeError("A2AAgentClient is not initialized. Use 'await A2AAgentClient.create(...)' or '__aenter__'.")
        return self._agent_card

    @property
    def supports_extended(self) -> bool:
        return bool(self.agent_card.supports_authenticated_extended_card)

    @property
    def client_url(self) -> str:
        return self.agent_card.url

    async def close(self) -> None:
        if self._owns_httpx_client and self._httpx_client is not None:
            await self._httpx_client.aclose()
        self._httpx_client = None

    async def __aenter__(self) -> "A2AAgentClient":
        if self._httpx_client is None:
            await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    def _ensure_ready(self) -> None:
        if self._client is None:
            raise RuntimeError("A2AAgentClient is not initialized. Use 'await A2AAgentClient.create(...)' or '__aenter__'.")

    async def send_text(self, text: str) -> dict[str, Any]:
        """
        Send a single-turn text message and return the response as JSON-serializable dict.
        """
        self._ensure_ready()
        assert self._client is not None

        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "message_id": uuid4().hex,
            }
        }
        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        response = await self._client.send_message(request)
        return response.model_dump(mode="json", exclude_none=True)

    async def start_task(self, text: str) -> tuple[dict[str, Any], str, str]:
        """
        Start a multi-turn interaction. Returns (response_json, task_id, context_id).
        """
        self._ensure_ready()
        assert self._client is not None

        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "message_id": uuid4().hex,
            }
        }
        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        response = await self._client.send_message(request)
        response_json = response.model_dump(mode="json", exclude_none=True)

        task_id = response.root.result.id
        context_id = response.root.result.context_id
        return response_json, task_id, context_id

    async def continue_task(self, text: str, task_id: str, context_id: str) -> dict[str, Any]:
        """
        Continue a multi-turn interaction identified by task/context identifiers.
        """
        self._ensure_ready()
        assert self._client is not None

        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "message_id": uuid4().hex,
                "task_id": task_id,
                "context_id": context_id,
            }
        }
        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        response = await self._client.send_message(request)
        return response.model_dump(mode="json", exclude_none=True)

    async def stream_text(self, text: str) -> AsyncIterator[dict[str, Any]]:
        """
        Stream chunks of the agent's response for a single-turn text message.
        Yields JSON-serializable dicts for each chunk.
        """
        self._ensure_ready()
        assert self._client is not None

        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "message_id": uuid4().hex,
            }
        }
        request = SendStreamingMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        stream = self._client.send_message_streaming(request)
        async for chunk in stream:
            yield chunk.model_dump(mode="json", exclude_none=True)


