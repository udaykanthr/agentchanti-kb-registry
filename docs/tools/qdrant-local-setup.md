---
id: "doc-002"
title: "Qdrant Local Setup Guide"
category: "doc"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - qdrant
  - vector-store
  - docker
  - embeddings
  - setup
---

# Qdrant Local Setup Guide

## Docker Setup

```bash
# Start Qdrant locally (data persisted in ./qdrant_storage)
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Verify it's running
curl http://localhost:6333/healthz  # returns {"status":"ok"}

# Stop
docker stop qdrant

# Remove (data persists in qdrant_storage/)
docker rm qdrant

# docker-compose.yml
# services:
#   qdrant:
#     image: qdrant/qdrant
#     ports:
#       - "6333:6333"
#       - "6334:6334"
#     volumes:
#       - ./qdrant_storage:/qdrant/storage
```

```bash
pip install qdrant-client
```

## Creating Collections

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, OptimizersConfigDiff
)

client = QdrantClient(host="localhost", port=6333)

# Create collection (recreate_collection deletes existing first)
client.recreate_collection(
    collection_name="kb_errors",
    vectors_config=VectorParams(
        size=1536,           # OpenAI text-embedding-3-small dimension
        distance=Distance.COSINE,  # or DOT, EUCLID
    ),
    # Optional: tune performance
    optimizers_config=OptimizersConfigDiff(
        indexing_threshold=20000,  # build HNSW index after this many vectors
    ),
)

# Check collection info
info = client.get_collection("kb_errors")
print(info.vectors_count)
print(info.status)  # 'green' = ready

# List all collections
collections = client.get_collections()
for col in collections.collections:
    print(col.name)

# Delete a collection
client.delete_collection("old_collection")
```

## Upserting Vectors

```python
from qdrant_client.models import PointStruct, UpdateStatus

# Single upsert
client.upsert(
    collection_name="kb_errors",
    points=[
        PointStruct(
            id=1,                          # must be int or UUID
            vector=[0.1, 0.2, ...],        # must match collection dimension
            payload={
                "error_id": "py-attr-001",
                "language": "python",
                "severity": "warning",
                "error_type": "AttributeError",
                "tags": ["attribute", "runtime"],
                "title": "Object has no attribute",
            }
        )
    ]
)

# Batch upsert (recommended for large datasets)
BATCH_SIZE = 100

def upsert_batch(points: list[PointStruct], collection: str):
    client.upsert(
        collection_name=collection,
        points=points,
        wait=True,  # wait for indexing before returning
    )

# Generate IDs consistently from string IDs
import hashlib

def str_to_id(s: str) -> int:
    """Deterministic integer ID from a string ID."""
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

point = PointStruct(
    id=str_to_id("py-attr-001"),
    vector=embedding,
    payload={"error_id": "py-attr-001", ...}
)
```

## Searching with Filters

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

# Simple exact match filter
results = client.search(
    collection_name="kb_errors",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="language", match=MatchValue(value="python")),
            FieldCondition(key="severity", match=MatchValue(value="warning")),
        ]
    ),
    limit=5,
    with_payload=True,   # include payload in results
    with_vectors=False,  # don't return vectors (saves bandwidth)
)

for hit in results:
    print(f"Score: {hit.score:.3f} | ID: {hit.payload['error_id']}")

# OR filter: language is python OR javascript
from qdrant_client.models import MatchAny
results = client.search(
    collection_name="kb_errors",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="language",
                match=MatchAny(any=["python", "javascript"])
            )
        ]
    ),
    limit=5,
)

# Scroll (retrieve without query vector — for listing)
records, next_offset = client.scroll(
    collection_name="kb_errors",
    scroll_filter=Filter(
        must=[FieldCondition(key="language", match=MatchValue(value="go"))]
    ),
    limit=100,
    with_payload=True,
)
```

## Snapshots

```python
# Create a snapshot (backup of collection)
snapshot_info = client.create_snapshot(collection_name="kb_errors")
print(snapshot_info.name)  # 'kb_errors-...-..-.tar'

# List snapshots
snapshots = client.list_snapshots("kb_errors")
for s in snapshots:
    print(s.name, s.size)

# Download snapshot (for backup)
# GET http://localhost:6333/collections/kb_errors/snapshots/{name}

# Restore from snapshot
client.recover_snapshot(
    collection_name="kb_errors",
    location="http://localhost:6333/collections/kb_errors/snapshots/snapshot_name.tar",
)
```

## Collection Management

```python
# Check if collection exists
def collection_exists(name: str) -> bool:
    try:
        client.get_collection(name)
        return True
    except Exception:
        return False

# Count vectors in collection
info = client.get_collection("kb_errors")
print(f"Vectors: {info.vectors_count}")

# Get a specific point by ID
point = client.retrieve(
    collection_name="kb_errors",
    ids=[str_to_id("py-attr-001")],
    with_payload=True,
)

# Delete points by ID
client.delete(
    collection_name="kb_errors",
    points_selector=[str_to_id("py-attr-001")],
)

# Delete points by filter (e.g., remove all 'info' severity entries)
from qdrant_client.models import FilterSelector
client.delete(
    collection_name="kb_errors",
    points_selector=FilterSelector(
        filter=Filter(must=[FieldCondition(key="severity", match=MatchValue(value="info"))])
    ),
)
```

## Common Configuration Issues

**GRPC port conflicts:** Qdrant exposes both REST (6333) and GRPC (6334). If port 6334 is in use, disable GRPC:
```bash
docker run -d -p 6333:6333 -e QDRANT__SERVICE__GRPC_PORT=0 qdrant/qdrant
```

**Connection refused:** Qdrant takes ~2 seconds to start. Add a health check before connecting:
```python
import time, httpx

def wait_for_qdrant(host: str = "localhost", port: int = 6333, timeout: int = 30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(f"http://{host}:{port}/healthz")
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError("Qdrant did not start in time")
```

**Dimension mismatch:** If you get "vector dimension mismatch," the embedding model changed. Recreate the collection and re-index all content.
