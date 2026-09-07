from __future__ import annotations

from typing import Any
import os

import httpx


class BackendClient:
    """
    Async HTTP client for the RetailMate transactional backend.

    Member 3 backend:
        http://127.0.0.1:8002

    Provides:
        - Product search
        - Inventory lookup
        - Order lookup
        - Return eligibility check
        - Return initiation
        - Exchange eligibility check
        - Exchange initiation
    """

    def __init__(self):
        self.base_url = os.getenv(
            "BACKEND_SERVICE_URL",
            "http://127.0.0.1:8002",
        ).rstrip("/")

        self.timeout = float(
            os.getenv("BACKEND_SERVICE_TIMEOUT", "10.0")
        )

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute an HTTP request and return the decoded JSON response.
        """

        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.request(
                    method,
                    url,
                    **kwargs,
                )

            if response.status_code >= 400:
                raise RuntimeError(
                    f"Backend service returned HTTP "
                    f"{response.status_code}: {response.text}"
                )

            return response.json()

        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Unable to connect to backend service at "
                f"{self.base_url}: {exc}"
            ) from exc

    # ============================================================
    # PRODUCTS
    # ============================================================

    async def search_products(
        self,
        query: str,
    ) -> Any:
        """
        Search products by name, category, or description.
        """

        if not query or not query.strip():
            raise ValueError("Product search query cannot be empty.")

        return await self._request(
            "GET",
            "/api/products/search",
            params={"q": query.strip()},
        )

    # ============================================================
    # INVENTORY
    # ============================================================

    async def get_inventory(
        self,
        product_id: str,
    ) -> Any:
        """
        Get inventory information for a product across stores.
        """

        if not product_id or not product_id.strip():
            raise ValueError("Product ID cannot be empty.")

        return await self._request(
            "GET",
            f"/api/inventory/{product_id.strip()}",
        )

    # ============================================================
    # ORDERS
    # ============================================================

    async def get_order(
        self,
        order_id: str,
    ) -> Any:
        """
        Retrieve an order and its items.
        """

        if not order_id or not order_id.strip():
            raise ValueError("Order ID cannot be empty.")

        return await self._request(
            "GET",
            f"/api/orders/{order_id.strip()}",
        )

    # ============================================================
    # RETURNS
    # ============================================================

    async def check_return(
        self,
        order_id: str,
        product_id: str,
    ) -> Any:
        """
        Check return eligibility.

        Backend:
            POST /api/returns/check

        Payload:
            {
                "order_id": "...",
                "product_id": "..."
            }
        """

        return await self._request(
            "POST",
            "/api/returns/check",
            json={
                "order_id": order_id,
                "product_id": product_id,
            },
        )

    async def initiate_return(
        self,
        order_id: str,
        product_id: str,
    ) -> Any:
        """
        Initiate an eligible return.

        Backend:
            POST /api/returns/initiate
        """

        return await self._request(
            "POST",
            "/api/returns/initiate",
            json={
                "order_id": order_id,
                "product_id": product_id,
            },
        )

    # ============================================================
    # EXCHANGES
    # ============================================================

    async def check_exchange(
        self,
        order_id: str,
        product_id: str,
        replacement_product_id: str,
    ) -> Any:
        """
        Check exchange eligibility including replacement stock.

        Backend:
            POST /api/exchanges/check
        """

        return await self._request(
            "POST",
            "/api/exchanges/check",
            json={
                "order_id": order_id,
                "product_id": product_id,
                "replacement_product_id": replacement_product_id,
            },
        )

    async def initiate_exchange(
        self,
        order_id: str,
        product_id: str,
        replacement_product_id: str,
    ) -> Any:
        """
        Initiate an eligible exchange.

        Backend:
            POST /api/exchanges/initiate
        """

        return await self._request(
            "POST",
            "/api/exchanges/initiate",
            json={
                "order_id": order_id,
                "product_id": product_id,
                "replacement_product_id": replacement_product_id,
            },
        )

    # ============================================================
    # HEALTH
    # ============================================================

    async def health_check(self) -> bool:
        """
        Check whether Member 3's backend is reachable.
        """

        try:
            response = await self._request(
                "GET",
                "/health",
            )

            return (
                isinstance(response, dict)
                and response.get("status") == "ok"
            )

        except (RuntimeError, ValueError):
            return False