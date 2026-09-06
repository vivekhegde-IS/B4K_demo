import asyncio
import sys
from pathlib import Path

# Add agent-service/app to Python path
APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from services.rag_client import RAGClient


async def main():
    print("=" * 60)
    print("RETAILMATE - MEMBER 4 → MEMBER 2 TEST")
    print("=" * 60)

    client = RAGClient()

    print("\nRAG service URL:")
    print(client.base_url)

    # ---------------------------------------------------------
    # 1. Health check
    # ---------------------------------------------------------
    print("\n[1] Checking RAG service health...")

    healthy = await client.health_check()

    if not healthy:
        print("❌ RAG SERVICE IS OFFLINE")
        print("Make sure Member 2's service is running on port 8000.")
        return

    print("✅ RAG SERVICE IS ONLINE")

    # ---------------------------------------------------------
    # 2. Send query
    # ---------------------------------------------------------
    print("\n[2] Sending test query to Member 2...")

    query = "What is the return policy?"

    print(f"Query: {query}")

    try:
        response = await client.query(
            query=query,
            language="en",
        )

    except Exception as exc:
        print("\n❌ RAG REQUEST FAILED")
        print(exc)
        return

    # ---------------------------------------------------------
    # 3. Display response
    # ---------------------------------------------------------
    print("\n[3] Response received!")
    print("=" * 60)

    print("Intent:")
    print(response.get("intent"))

    print("\nAnswer:")
    print(response.get("answer"))

    print("\nConfidence:")
    print(response.get("confidence"))

    print("\nLanguage:")
    print(response.get("language"))

    print("\nAction Required:")
    print(response.get("action_required"))

    print("\nAction:")
    print(response.get("action"))

    print("\nMissing Information:")
    print(response.get("missing_information"))

    # ---------------------------------------------------------
    # 4. Products
    # ---------------------------------------------------------
    print("\nProducts:")

    products = response.get("products", [])

    if products:
        for product in products:
            print(product)
    else:
        print("No products returned.")

    # ---------------------------------------------------------
    # 5. Sources
    # ---------------------------------------------------------
    print("\nSources:")

    sources = response.get("sources", [])

    if sources:
        for source in sources:
            print(source)
    else:
        print("No sources returned.")

    print("\n" + "=" * 60)
    print("✅ MEMBER 4 → MEMBER 2 CONNECTION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())