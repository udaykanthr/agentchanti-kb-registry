---
id: "adr-004"
title: "ADR-004: Hybrid KB Architecture — Graph + Vectors"
category: "adr"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - architecture
  - knowledge-base
  - graph
  - vectors
  - hybrid-search
---

# ADR-004: Hybrid KB Architecture — Graph + Vectors

## Status

Accepted

## Context

AgentChanti's knowledge base serves two fundamentally different types of queries:

**Type 1: Structural/Exact queries** (requires precision)
- "What functions does `UserService.create` call?"
- "What imports does `orders.py` have?"
- "Find all subclasses of `BaseException`"
- "What changed between these two versions of a function?"

These queries require exact, deterministic answers. Semantics don't help here — either `orders.py` imports `redis` or it doesn't.

**Type 2: Semantic/Relevance queries** (requires flexibility)
- "Find patterns similar to what the user is trying to do"
- "Find error entries that match this stack trace"
- "What documentation is relevant to this authentication bug?"
- "Find code in the repository that does something similar to X"

These queries require semantic understanding. An exact keyword match would miss valid results ("async timeout" should match entries about `asyncio.wait_for` and `asyncio.timeout`).

Both query types are critical to AgentChanti's utility. Using only one storage system would leave one type of query significantly impaired.

## Decision

AgentChanti will use a **two-layer knowledge base architecture**:

1. **Layer 1: Code Graph (NetworkX)** — for structural, exact, navigational queries
2. **Layer 2: Vector Store (Qdrant)** — for semantic, relevance, similarity queries

These two layers are **complementary, not substitutes**. Neither will be replaced by the other.

```
Query → Router → ┌─────────────────────────────────────────┐
                  │           Query Types                    │
                  │                                          │
                  │  Structural?  → Code Graph (NetworkX)    │
                  │                  - Call graphs           │
                  │                  - Import deps           │
                  │                  - Inheritance trees     │
                  │                                          │
                  │  Semantic?    → Vector Store (Qdrant)    │
                  │                  - Error matching        │
                  │                  - Pattern similarity    │
                  │                  - Doc relevance         │
                  │                                          │
                  │  Hybrid?      → Both, merge results      │
                  └─────────────────────────────────────────┘
```

**Hybrid retrieval example:**

```python
async def find_relevant_context(query: str, language: str) -> list[KBResult]:
    """
    Combines structural and semantic search results for LLM context.
    """
    results = []

    # Semantic: find similar error entries and patterns
    semantic_hits = await qdrant_client.search(
        collection_name="kb_errors",
        query_vector=await embed(query),
        query_filter=Filter(
            must=[FieldCondition(key="language", match=MatchValue(value=language))]
        ),
        limit=5,
    )
    results.extend(semantic_hits)

    # Structural: if query mentions a specific function, get its call graph
    if function_name := extract_function_name(query):
        callees = nx.descendants(code_graph, function_name)
        for callee in list(callees)[:10]:
            results.append(code_graph.nodes[callee])

    # Deduplicate and rank by relevance
    return rank_and_deduplicate(results)
```

## Consequences

**Positive:**
- Each layer is used for what it does best — no forcing square pegs into round holes
- Structural queries are O(1) or O(log n) graph lookups — extremely fast
- Semantic queries use vector similarity — captures intent even with different terminology
- The two layers are independently indexable — updating the KB doesn't require re-building the code graph, and re-indexing the code doesn't require updating error dictionaries
- Testable independently — unit tests for graph traversal don't need Qdrant running

**Negative:**
- Two systems to maintain, monitor, and serialize
- Hybrid query results require a merging/ranking step
- Two sets of data to keep in sync when code changes (the graph and the embeddings)

**What this is NOT:**
- The vector store does **not** replace the code graph for structural queries. Vector search on function names would be probabilistic and wrong — exact graph traversal is required.
- The code graph does **not** replace the vector store for semantic search. Keyword matching in graph node attributes would miss semantically related results.

## Architecture Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    Code Graph Layer                      │
│  Input: Source code files (parsed by Tree-sitter)       │
│  Storage: NetworkX DiGraph + pickle                     │
│  Queries: navigational, structural, exact               │
│  Examples: callers, callees, imports, class hierarchy   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Vector Store Layer                     │
│  Input: KB registry files (.yml errors, .md patterns)   │
│  Storage: Qdrant collections                            │
│  Queries: semantic, similarity, relevance               │
│  Examples: error matching, doc search, pattern search   │
└─────────────────────────────────────────────────────────┘
```

## Alternatives Considered

### Single layer: vectors only
- **Rejected**: Structural queries ("what does this function call?") cannot be answered with vector search alone. Graph traversal provides O(1) answers to questions that would require O(N) vector comparisons and post-filtering.

### Single layer: graph only
- **Rejected**: Semantic similarity search is not achievable with graph lookups. Finding "which error entry matches this stack trace" requires embedding-based similarity — graph node attributes don't capture this.

### Relational database for both
- **Rejected**: SQL supports neither efficient graph traversal (without recursive CTEs) nor vector similarity search (without extensions like pgvector). Two separate concerns warrant two specialized tools.
