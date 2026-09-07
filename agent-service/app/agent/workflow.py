from __future__ import annotations

from typing import Any, Optional
import logging
import time
from datetime import datetime, timezone

from app.agent.tools import AgentTools

logger = logging.getLogger(__name__)


class AgentWorkflow:
    """
    Main orchestration layer for Member 4.

    Responsibilities:
    - Accept text/transcribed user input.
    - Forward the request to Member 2's RAG/AI assistant.
    - Preserve the structured response.
    - Return a normalized result for the frontend/voice layer.

    Member 2 remains responsible for:
    - Intent detection
    - RAG retrieval
    - Policy answers
    - Inventory/product handling
    - Return/exchange orchestration
    - Transactional communication with Member 3
    """

    def __init__(self):
        self.tools = AgentTools()

    async def process(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Process one user request through Member 2.

        The response is intentionally kept structured so the
        frontend can display the answer and action information,
        while the voice layer can synthesize the answer text.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        pipeline_started = time.perf_counter()
        pipeline_started_at = datetime.now(timezone.utc).isoformat()

        result = await self.tools.query_rag(
            query=query.strip(),
            user_id=user_id,
            session_id=session_id,
            language=language,
        )

        timing = {
            **result.pop("_agent_timing", {}),
            **result.pop("timing", {}),
        }
        timing.update({
            "agent_request_start": pipeline_started_at,
            "agent_response_end": datetime.now(timezone.utc).isoformat(),
            "agent_latency_ms": round(
                (time.perf_counter() - pipeline_started) * 1000,
                2,
            ),
        })

        logger.info(
            "[Voice Pipeline] RAG: %.2f ms | TOTAL_AGENT: %.2f ms",
            timing.get("rag_latency_ms", 0.0),
            timing["agent_latency_ms"],
        )

        return {
            "success": True,
            "query": query.strip(),
            "intent": result.get("intent"),
            "answer": result.get("answer", ""),
            "products": result.get("products", []),
            "sources": result.get("sources", []),
            "action_required": result.get("action_required", False),
            "action": result.get("action"),
            "confidence": result.get("confidence", 0.0),
            "missing_information": result.get(
                "missing_information",
                [],
            ),
            "session_id": result.get("session_id"),
            "language": result.get(
                "language",
                language,
            ),
            "timing": timing,
        }