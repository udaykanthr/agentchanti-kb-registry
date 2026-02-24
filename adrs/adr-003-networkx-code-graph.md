---
id: "adr-003"
title: "ADR-003: Use NetworkX for Local Code Graph"
category: "adr"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - graph
  - networkx
  - code-analysis
  - call-graph
  - local-first
---

# ADR-003: Use NetworkX for Local Code Graph

## Status

Accepted

## Context

AgentChanti builds a code graph to represent relationships between code entities: function calls, class inheritance, module imports, and variable usage. The graph enables:

1. Call graph traversal ("what functions does `process_order` call transitively?")
2. Dependency analysis ("what modules does this file depend on?")
3. Impact analysis ("what code is affected if I change this function?")
4. Dead code detection ("what functions are never called?")

Requirements:
- Pure Python — no external database or service needed
- Serializable to disk — graph must persist between sessions without a running server
- Supports directed graphs with attributes on both nodes and edges
- BFS/DFS traversal, shortest path, predecessors/successors
- Fast enough for repositories up to ~50,000 nodes (functions, classes, modules)
- Zero infrastructure — should work offline, in CI, and on a developer laptop

## Decision

We will use **NetworkX** for all in-memory code graph operations, serialized to disk using Python's `pickle` module.

```python
import networkx as nx
import pickle
from pathlib import Path

# Create directed graph for call relationships
G = nx.DiGraph()

# Add nodes with rich metadata
G.add_node('myapp.services.OrderService.process',
    type='method',
    file='src/services.py',
    line=42,
    language='python',
    is_async=True,
)

# Add edges representing call relationships
G.add_edge(
    'myapp.services.OrderService.process',
    'myapp.repositories.OrderRepository.save',
    edge_type='calls',
    line=58,
)

# Traversal: find all transitive callees
callees = nx.descendants(G, 'myapp.services.OrderService.process')

# Traversal: find all callers of a function (reverse graph)
R = G.reverse()
callers = nx.descendants(R, 'myapp.repositories.OrderRepository.save')

# Shortest path between two functions
path = nx.shortest_path(G, 'main', 'low_level_function')

# Detect cycles (circular dependencies)
cycles = list(nx.simple_cycles(G))

# Serialization: save graph to disk
graph_path = Path('.agentchanti/code_graph.pkl')
with graph_path.open('wb') as f:
    pickle.dump(G, f)

# Reload
with graph_path.open('rb') as f:
    G = pickle.load(f)
```

## Consequences

**Positive:**
- Zero infrastructure — pure Python, no server, no Docker required
- Entire graph serializes to a single `.pkl` file — trivial to persist and reload
- NetworkX implements all required algorithms: BFS, DFS, shortest path, cycle detection, topological sort
- Rich node and edge attribute support — can store any Python dict as metadata
- Very fast for graphs up to ~100,000 nodes (in-memory, no I/O during traversal)
- Battle-tested: used in scientific computing, dependency analysis tools, and research

**Negative:**
- Not suitable for graphs with millions of nodes (in-memory limitation)
- Pickle format is not human-readable and is not interoperable across Python versions
- No built-in query language — must write Python code for complex graph queries
- Concurrent writes require explicit locking (not a concern for current single-agent use)

**Risks:**
- Large repositories (>200K nodes) may cause memory pressure (mitigation: partition graph by module, lazy-load subgraphs on demand)
- Pickle files can break on Python version upgrades (mitigation: store graph schema version, invalidate and rebuild on mismatch)

## Alternatives Considered

### Neo4j
- **Pros**: Industry-standard graph database, Cypher query language, excellent tooling, browser UI for visualization
- **Cons**: Requires a running JVM process, significant memory overhead, complex to set up locally, requires Docker or native installation, Cypher must be learned
- **Why rejected**: Violates the local-first, zero-infrastructure requirement. A graph database is overkill for a single-user developer tool that fits in RAM

### DGraph
- **Pros**: GraphQL-like query language, distributed, scalable
- **Cons**: Even heavier infrastructure than Neo4j, designed for distributed use cases, not local-first
- **Why rejected**: Same concerns as Neo4j, with additional complexity

### ArangoDB
- **Pros**: Multi-model (document + graph + key-value), AQL query language
- **Cons**: Requires a running server, complex setup
- **Why rejected**: Infrastructure overhead is not justified for local single-user use

### SQLite Adjacency List
- **Pros**: No external dependencies beyond Python stdlib, human-readable, SQL queries
- **Cons**: Graph algorithms (BFS, shortest path) must be implemented manually in SQL or Python, no built-in attribute support for edges, graph traversal is verbose and slow in SQL
- **Why rejected**: Implementing BFS and DFS in SQLite is significantly more work than using NetworkX, with no performance benefit for our scale
