from typing import Any, Optional
import os

import httpx


class RAGClient:
    """
    HTTP client for the RetailMate RAG service.

    Member 4 -> Member 2
    """

    def __init__(self):
        self.base_url = os.getenv(
            "RAG_SERVICE_URL",
            "http://127.0.0.1:8000"
        ).rstrip("/")

        self.timeout = float(
            os.getenv("RAG_SERVICE_TIMEOUT", "30.0")
        )

    async def health_check(self) -> bool:
        """Check whether the RAG service is available."""

        url = f"{self.base_url}/health"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)

            return response.status_code == 200

        except httpx.RequestError:
            return False

    async def query(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Send a natural-language query to Member 2's RAG service.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        payload = {
            "query": query,
            "user_id": user_id,
            "session_id": session_id,
            "language": language,
        }

        url = f"{self.base_url}/api/assistant/query"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                )

            if response.status_code >= 400:
                raise RuntimeError(
                    f"RAG service returned HTTP {response.status_code}: "
                    f"{response.text}"
                )

            return response.json()

        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Unable to connect to RAG service at {self.base_url}: {exc}"
            ) from exc