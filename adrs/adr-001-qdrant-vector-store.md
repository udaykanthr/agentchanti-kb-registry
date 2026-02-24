---
id: "adr-001"
title: "ADR-001: Use Qdrant for Local Vector Storage"
category: "adr"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - vector-store
  - qdrant
  - embeddings
  - local-first
---

# ADR-001: Use Qdrant for Local Vector Storage

## Status

Accepted

## Context

AgentChanti requires a vector store to support semantic search over the knowledge base — specifically for finding semantically similar errors, patterns, and documentation to a user's query. The vector store must:

1. Run locally without requiring a cloud subscription or API key
2. Support efficient payload-based filtering (e.g., filter by language, category, severity)
3. Scale to at least 100,000 vectors without significant performance degradation
4. Be runnable via Docker in a single command for development and CI
5. Support named collections (errors, patterns, docs) to organize the KB content
6. Be accessible from Python without complex infrastructure setup

## Decision

We will use **Qdrant** as the vector store for AgentChanti's knowledge base.

Qdrant will be deployed as a local Docker container during development and as a sidecar container in production deployments. The Python client library (`qdrant-client`) will manage collections and CRUD operations.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Initialize local client
client = QdrantClient(host="localhost", port=6333)

# Create a collection
client.recreate_collection(
    collection_name="kb_errors",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Upsert with rich payload for filtering
client.upsert(
    collection_name="kb_errors",
    points=[
        PointStruct(
            id=1,
            vector=embedding_vector,
            payload={
                "error_id": "py-attr-001",
                "language": "python",
                "severity": "warning",
                "error_type": "AttributeError",
                "tags": ["attribute", "runtime"],
            }
        )
    ]
)

# Search with payload filter
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="kb_errors",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[FieldCondition(key="language", match=MatchValue(value="python"))]
    ),
    limit=5,
)
```

## Consequences

**Positive:**
- Single Docker command to start: `docker run -p 6333:6333 qdrant/qdrant`
- Rich payload filtering — can filter by language, severity, category without post-processing
- Named collections keep KB content organized and independently searchable
- GRPC interface provides high throughput; REST interface enables easy debugging
- Native support for snapshots — KB state is easily backed up and restored
- Qdrant's Rust implementation provides excellent performance without a JVM
- Active open-source development with frequent releases

**Negative:**
- Adds a Docker dependency (vs. pure-Python alternatives like ChromaDB or FAISS)
- Requires a running server process (cannot embed in-process like FAISS)
- Qdrant is a relatively new project compared to FAISS or Pinecone

**Risks:**
- If the Docker container is not running, AgentChanti's semantic search will fail (mitigation: graceful degradation to keyword search)
- Schema migrations require re-indexing collections (mitigation: version collections, keep source .yml/.md files as source of truth)

## Alternatives Considered

### ChromaDB
- **Pros**: Pure Python, embeds in-process (no Docker needed), simple API
- **Cons**: Slower performance at scale, limited payload filtering capabilities, less battle-tested for production workloads
- **Why rejected**: Payload filtering limitations would force post-filter in Python, reducing performance at scale

### FAISS (Facebook AI Similarity Search)
- **Pros**: Extremely fast, battle-tested, integrates with LangChain
- **Cons**: No built-in persistence without wrapping, no payload filtering (must maintain a separate metadata store), C++ library with Python bindings that can be painful to install
- **Why rejected**: No native payload filtering; would require a parallel SQLite/dict for metadata, adding complexity

### Weaviate
- **Pros**: Full-featured, GraphQL API, strong filtering
- **Cons**: Heavy Java-based infrastructure, higher resource usage, more complex to self-host
- **Why rejected**: Too heavyweight for a local developer tool; Qdrant achieves the same filtering with lower overhead

### Pinecone (cloud)
- **Pros**: Fully managed, no infrastructure to maintain
- **Cons**: Cloud-only — violates the local-first requirement, adds cost and data privacy concerns
- **Why rejected**: Requires network access; violates the local-first design goal
