from typing import Any, Optional

from app.services.rag_client import RAGClient
from app.services.backend_client import BackendClient

class AgentTools:
    """
    Tool layer for the RetailMate agent.

    Member 4 uses this layer to access:
    - Member 2: RAG + intent + policy/assistant responses
    - Member 3: inventory, orders, returns and exchanges

    The workflow should call these tools instead of directly
    communicating with the underlying services.
    """

    def __init__(self):
        self.rag = RAGClient()
        self.backend = BackendClient()

    # ============================================================
    # MEMBER 2 — RAG / AI ASSISTANT
    # ============================================================

    async def query_rag(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Send a natural-language query to Member 2's RAG service.
        """
        return await self.rag.query(
            query=query,
            user_id=user_id,
            session_id=session_id,
            language=language,
        )

    # ============================================================
    # MEMBER 3 — INVENTORY
    # ============================================================

    async def search_products(self, query: str) -> Any:
        """
        Search the product catalog.
        """
        return await self.backend.search_products(query)

    async def get_inventory(self, product_id: str) -> Any:
        """
        Get inventory information for a product.
        """
        return await self.backend.get_inventory(product_id)

    # ============================================================
    # MEMBER 3 — ORDERS
    # ============================================================

    async def get_order(self, order_id: str) -> Any:
        """
        Retrieve order information.
        """
        return await self.backend.get_order(order_id)

    # ============================================================
    # MEMBER 3 — RETURNS
    # ============================================================

    async def check_return(
        self,
        order_id: str,
        product_id: str,
    ) -> Any:
        """
        Check whether a product is eligible for return.
        """
        return await self.backend.check_return(
            order_id=order_id,
            product_id=product_id,
        )

    async def initiate_return(
        self,
        order_id: str,
        product_id: str,
    ) -> Any:
        """
        Initiate an approved return.
        """
        return await self.backend.initiate_return(
            order_id=order_id,
            product_id=product_id,
        )

    # ============================================================
    # MEMBER 3 — EXCHANGES
    # ============================================================

    async def check_exchange(
        self,
        order_id: str,
        product_id: str,
        replacement_product_id: str,
    ) -> Any:
        """
        Check whether an exchange is eligible.
        """
        return await self.backend.check_exchange(
            order_id=order_id,
            product_id=product_id,
            replacement_product_id=replacement_product_id,
        )

    async def initiate_exchange(
        self,
        order_id: str,
        product_id: str,
        replacement_product_id: str,
    ) -> Any:
        """
        Initiate an approved exchange.
        """
        return await self.backend.initiate_exchange(
            order_id=order_id,
            product_id=product_id,
            replacement_product_id=replacement_product_id,
        )