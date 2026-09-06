# RetailMate RAG Service

AI-powered Retrieval-Augmented Generation (RAG) service for the RetailMate retail assistant. Combines semantic document retrieval, intent detection, and backend API integration to answer product, policy, inventory, and transactional queries.

## Architecture

```
User Query
    │
    ▼
┌──────────────┐
│ Intent       │ ← Rule-based classifier
│ Detector     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│              Assistant Orchestrator           │
│                                              │
│  POLICY_QUERY ──► RAG Retriever (ChromaDB)   │
│  INVENTORY   ──► Backend API + RAG           │
│  LOCATION    ──► Backend API + RAG           │
│  RETURN_REQ  ──► Backend API (check/initiate)│
│  EXCHANGE    ──► Backend API (check/initiate)│
│  GENERAL     ──► RAG Retriever               │
└──────────────────────────────────────────────┘
       │
       ▼
  Structured JSON Response
```

### Source-of-Truth Separation

| Data Type | Source | Method |
|-----------|--------|--------|
| Policy rules, return windows, conditions | Policy PDF via RAG/ChromaDB | Semantic retrieval |
| Live inventory, stock quantities | Member 3 backend | HTTP API |
| Order details, eligibility | Member 3 backend | HTTP API |
| Return/exchange transactions | Member 3 backend | HTTP API |
| Store layout, hours | Store info via RAG | Semantic retrieval |
| Product catalog (static) | products.json via RAG | Semantic retrieval |

## Policy PDF

The authoritative policy document is located at:

```
rag-service/knowledge_base/order_cancellation_return_policy.pdf
```

This PDF contains **category-specific return windows** (e.g., Lifestyle/Footwear = 10 days). The system does **not** hardcode a universal return period.

## Installation

```bash
cd rag-service

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy the example and adjust as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_HOST` | `0.0.0.0` | Service bind address |
| `RAG_PORT` | `8001` | Service port |
| `BACKEND_URL` | `http://localhost:8002` | Member 3 backend URL |
| `CHROMA_PERSIST_DIRECTORY` | `./data/chroma` | ChromaDB storage path |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Sentence Transformer model |
| `TOP_K` | `5` | Number of retrieval results |
| `CHUNK_SIZE` | `500` | Chunk size in characters |
| `CHUNK_OVERLAP` | `75` | Chunk overlap in characters |

## Indexing the Knowledge Base

Before starting the service, index the knowledge base into ChromaDB:

```bash
cd rag-service
python -m app.rag.index
```

This processes:
1. **Policy PDF** → semantic chunks → ChromaDB
2. **Store information** → chunks → ChromaDB
3. **Product catalog** → per-product documents → ChromaDB

Indexing is **idempotent** — running it multiple times does not create duplicates.

## ChromaDB

The vector database is persisted to `./data/chroma` and is **not committed to Git**. The `.gitignore` excludes `rag-service/data/`.

## Running the Service

```bash
cd rag-service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

The service will be available at `http://localhost:8001`.

## API Endpoint

### `GET /health`

```json
{"status": "ok", "service": "retailmate-rag"}
```

### `POST /api/assistant/query`

**Request:**

```json
{
    "query": "What is the return window for footwear?",
    "user_id": "demo-user",
    "session_id": "session-001",
    "language": "en"
}
```

**Response:**

```json
{
    "intent": "POLICY_QUERY",
    "answer": "Based on the Order Cancellation and Return Policy:\n\nLifestyle: Watch, T-Shirt, Footwear, Sari... 10 days Refund, Replacement or Exchange",
    "products": [],
    "sources": [
        {
            "title": "Order Cancellation and Return Policy",
            "source": "order_cancellation_return_policy.pdf",
            "page": 3,
            "relevance": 0.85
        }
    ],
    "action_required": false,
    "action": null,
    "confidence": 0.85,
    "missing_information": [],
    "session_id": "session-001",
    "language": "en"
}
```

## Backend Integration

The RAG service communicates with Member 3's backend at `http://localhost:8002` via HTTP only. It **never** accesses the database directly.

Backend endpoints used:
- `GET /api/products/search?q=...`
- `GET /api/inventory/{product_id}`
- `GET /api/orders/{order_id}`
- `POST /api/returns/check`
- `POST /api/returns/initiate`
- `POST /api/exchanges/check`
- `POST /api/exchanges/initiate`

## Testing

```bash
cd rag-service
pytest tests/ -v
```

Tests use `respx` to mock backend HTTP calls — no real backend needed for unit tests.

## Known Limitations

1. Intent detection uses rule-based pattern matching (not ML/LLM) — suitable for MVP.
2. Policy answers present retrieved text rather than generating new natural-language summaries (no LLM generation step).
3. The embedding model (`all-MiniLM-L6-v2`) runs on CPU; first load takes a few seconds.
4. Product search through the backend depends on Member 3's search implementation.
