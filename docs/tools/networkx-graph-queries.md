---
id: "doc-003"
title: "NetworkX Graph Queries Guide"
category: "doc"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - networkx
  - graph
  - code-analysis
  - traversal
  - call-graph
---

# NetworkX Graph Queries Guide

## Creating Directed Graphs

```python
import networkx as nx

# Directed graph (for call graphs, import dependencies)
G = nx.DiGraph()

# Undirected graph (for similarity relationships)
G_undirected = nx.Graph()

# Multi-digraph: allows multiple edges between same pair of nodes
# (useful for different relationship types)
G_multi = nx.MultiDiGraph()
```

## Adding Nodes with Attributes

```python
# Single node with metadata
G.add_node('myapp.services.UserService.create',
    type='method',
    file='src/services/user.py',
    line=42,
    language='python',
    is_async=True,
    class_name='UserService',
    module='myapp.services',
)

# Multiple nodes at once
G.add_nodes_from([
    ('myapp.models.User', {'type': 'class', 'file': 'src/models.py', 'line': 10}),
    ('myapp.models.Order', {'type': 'class', 'file': 'src/models.py', 'line': 45}),
])

# Access node attributes
attrs = G.nodes['myapp.services.UserService.create']
print(attrs['line'])        # 42
print(attrs.get('tags', []))  # safe access with default

# Iterate over all nodes with attributes
for node, data in G.nodes(data=True):
    if data.get('type') == 'method':
        print(f"{node}: line {data.get('line')}")
```

## Adding Edges with Attributes

```python
# Add directed edge: caller → callee
G.add_edge(
    'myapp.services.UserService.create',
    'myapp.repositories.UserRepository.save',
    edge_type='calls',
    line=58,
    weight=1.0,
)

G.add_edge(
    'myapp.services.UserService.create',
    'myapp.services.EmailService.send_welcome',
    edge_type='calls',
    line=65,
)

# Access edge attributes
edge_data = G['myapp.services.UserService.create']['myapp.repositories.UserRepository.save']
print(edge_data['line'])  # 58

# Iterate over edges with attributes
for u, v, data in G.edges(data=True):
    print(f"{u} → {v} [{data.get('edge_type')}]")
```

## BFS/DFS Traversal

```python
# BFS: breadth-first traversal from a source node
bfs_nodes = list(nx.bfs_tree(G, 'myapp.services.UserService.create').nodes())
# Returns nodes in BFS order (including source)

# DFS: depth-first traversal
dfs_nodes = list(nx.dfs_tree(G, 'myapp.services.UserService.create').nodes())

# All descendants (transitive callees)
descendants = nx.descendants(G, 'myapp.services.UserService.create')
print(f"UserService.create transitively calls {len(descendants)} functions")

# All ancestors (transitive callers)
ancestors = nx.ancestors(G, 'myapp.repositories.UserRepository.save')
print(f"UserRepository.save is transitively called by {ancestors}")

# BFS with depth limit
from networkx.algorithms.traversal.breadth_first_search import bfs_edges
direct_callees = {v for u, v in bfs_edges(G, 'myapp.services.UserService.create', depth_limit=1)}
```

## Shortest Path

```python
# Shortest path between two nodes
try:
    path = nx.shortest_path(G, 'main', 'myapp.repositories.UserRepository.save')
    print(" → ".join(path))
except nx.NetworkXNoPath:
    print("No path exists between these nodes")
except nx.NodeNotFound as e:
    print(f"Node not found: {e}")

# All shortest paths
all_paths = list(nx.all_shortest_paths(G, 'main', 'UserRepository.save'))

# Path length (number of edges)
length = nx.shortest_path_length(G, 'main', 'UserRepository.save')

# Dijkstra (weighted) — useful if edges have weights
weighted_path = nx.dijkstra_path(G, 'main', 'save', weight='weight')
```

## Predecessors and Successors

```python
# Direct successors (immediate callees)
callees = list(G.successors('myapp.services.UserService.create'))

# Direct predecessors (immediate callers)
callers = list(G.predecessors('myapp.repositories.UserRepository.save'))

# Check if an edge exists
if G.has_edge('UserService.create', 'UserRepository.save'):
    print("Direct call relationship exists")

# In-degree and out-degree
print(G.in_degree('UserRepository.save'))   # number of callers
print(G.out_degree('UserService.create'))   # number of direct callees

# Nodes sorted by number of callers (most-called functions)
hotspots = sorted(G.nodes(), key=lambda n: G.in_degree(n), reverse=True)[:10]
```

## Serialization with Pickle

```python
import pickle
from pathlib import Path

GRAPH_PATH = Path('.agentchanti/code_graph.pkl')

def save_graph(G: nx.DiGraph, path: Path = GRAPH_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as f:
        pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Graph saved: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

def load_graph(path: Path = GRAPH_PATH) -> nx.DiGraph:
    if not path.exists():
        return nx.DiGraph()
    with path.open('rb') as f:
        return pickle.load(f)

# Alternative: GraphML (human-readable XML, slower)
nx.write_graphml(G, 'graph.graphml')
G2 = nx.read_graphml('graph.graphml')

# JSON (node/edge data must be JSON-serializable)
from networkx.readwrite import json_graph
import json
data = json_graph.node_link_data(G)
json.dump(data, open('graph.json', 'w'))
G3 = json_graph.node_link_graph(json.load(open('graph.json')))
```

## Performance Tips for Large Graphs

```python
# 1. Use integer node IDs instead of long strings for large graphs
# Map strings to ints, keep a reverse lookup
node_index = {}
reverse_index = {}
counter = 0

def get_node_id(name: str) -> int:
    global counter
    if name not in node_index:
        node_index[name] = counter
        reverse_index[counter] = name
        counter += 1
    return node_index[name]

# 2. Batch add operations (faster than individual add_node/add_edge calls)
nodes_to_add = [
    (get_node_id(name), attrs) for name, attrs in node_data.items()
]
G.add_nodes_from(nodes_to_add)

edges_to_add = [
    (get_node_id(u), get_node_id(v), attrs) for u, v, attrs in edge_data
]
G.add_edges_from(edges_to_add)

# 3. For read-only traversal, freeze the graph (prevents accidental mutation)
frozen = nx.freeze(G)

# 4. Subgraph views (lazy, no copy)
subgraph = G.subgraph(['node1', 'node2', 'node3'])  # view, not copy

# 5. Detect cycles early (before traversal algorithms that assume DAG)
if not nx.is_directed_acyclic_graph(G):
    cycles = list(nx.simple_cycles(G))
    print(f"Found {len(cycles)} cycles")
```
