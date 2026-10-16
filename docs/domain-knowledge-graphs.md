# Capturing Domain Knowledge

yggdrasil's graph is primarily an **orchestration graph**: agents, tools, prompts, and context wired together so the runtime can execute and explain them. But the same store can hold a second, independent layer — a **domain knowledge graph** of whatever entities *your* application cares about (customers and orders, papers and citations, API endpoints and their monitors, …).

This page shows how to model any domain in that layer using three additions that are deliberately **domain-agnostic** — yggdrasil never interprets them:

| Primitive | Purpose |
|---|---|
| `Node.domain_type: str \| None` | Tags a node as a domain entity of some kind (`"customer"`, `"paper"`, `"endpoint"`). |
| `EdgeType.RELATES` + `Edge.relation: str \| None` | A neutral edge type whose **label** (`"ordered"`, `"cites"`, `"checks"`) carries the relationship meaning. |
| Store filters: `list_nodes(domain_type=…)`, `list_edges(relation=…)`, `get_edges(…, relation=…)` | Query the domain layer without scanning the orchestration nodes. |

The key idea: **you never edit yggdrasil's `NodeType` / `EdgeType` enums to add a domain.** Entities are `CONTEXT` nodes carrying a `domain_type`; relationships are `RELATES` edges carrying a `relation` label. The vocabulary lives in *data*, so the framework stays general and your domain stays yours.

---

## The modeling recipe (any domain)

1. **List your entity kinds** → each becomes a `domain_type` string.
2. **List your relationships** → each becomes a `relation` label on a `RELATES` edge.
3. **Create one `ContextNode` per entity instance**, with `domain_type` set and the payload in `attributes`.
4. **Connect them with `Edge.relates(src, dst, relation=…)`.**
5. **Query** with the domain filters; **traverse** with `neighbors` / `get_edges`.

That is the whole method. Everything below is detail.

---

## A worked example

Model a tiny e-commerce domain: customers place orders; orders contain products.

```python
import asyncio
from yggdrasil_lm import NetworkXGraphStore, ContextNode, Edge, EdgeType

async def main():
    store = NetworkXGraphStore()

    # 1-3. Entities: one ContextNode per instance, domain_type set, data in attributes.
    alice  = ContextNode(name="Alice",   domain_type="customer", attributes={"tier": "gold"})
    order1 = ContextNode(name="#1001",   domain_type="order",    attributes={"total": 90})
    widget = ContextNode(name="Widget",  domain_type="product",  attributes={"sku": "W-1"})
    for n in (alice, order1, widget):
        await store.upsert_node(n)

    # 4. Relationships: RELATES edges with a domain `relation` label.
    await store.upsert_edge(Edge.relates(alice.node_id,  order1.node_id, relation="placed"))
    await store.upsert_edge(Edge.relates(order1.node_id, widget.node_id, relation="contains"))

    # 5. Query the domain layer.
    customers = await store.list_nodes(domain_type="customer")          # [Alice]
    placed    = await store.list_edges(relation="placed")               # [Alice -placed-> #1001]
    in_order  = await store.get_edges(order1.node_id, direction="out", relation="contains")
    print([c.name for c in customers], len(placed), len(in_order))

asyncio.run(main())
```

The same store could simultaneously hold the agents and tools that *process* these orders — the two layers coexist and never collide, because every query is scoped by `domain_type` / `relation`.

---

## Grounding it: an API-catalog domain

A common shape for this layer — capturing how an API's **endpoints**, **SDK methods**, and **monitors** relate:

```python
endpoint   = ContextNode(name="get_user",         domain_type="endpoint",   attributes={"path": "/users/{id}"})
sdk_method = ContextNode(name="client.get_user",  domain_type="sdk_method", attributes={"language": "python"})
monitor    = ContextNode(name="get_user_latency", domain_type="monitor",    attributes={"expr": "p95 < 300ms"})
for n in (endpoint, sdk_method, monitor):
    await store.upsert_node(n)

await store.upsert_edge(Edge.relates(sdk_method.node_id, endpoint.node_id, relation="wraps"))
await store.upsert_edge(Edge.relates(monitor.node_id,    endpoint.node_id, relation="checks"))
```

Now the diagnostic questions become one-line queries:

```python
# Endpoints that no monitor checks ("unmonitored" candidates)
endpoints = await store.list_nodes(domain_type="endpoint")
orphans = [f for f in endpoints
           if not await store.get_edges(f.node_id, direction="in", relation="checks")]

# Endpoints with >1 monitor checking them ("duplicate monitor" candidates)
crowded = [f for f in endpoints
           if len(await store.get_edges(f.node_id, direction="in", relation="checks")) > 1]

# SDK methods wrapping an endpoint that no longer exists ("stale binding")
# -> follow each SDK method's `wraps` edge and check the endpoint node still resolves.
```

---

## Traversal

`get_edges(node_id, direction=…, relation=…)` is the primary domain-traversal primitive: it is the one that filters by `relation` **and** lets you choose `direction="in" | "out" | "both"`. Since relationship direction is meaningful (a *monitor* `checks` an *endpoint*, so the edge points monitor → endpoint), pick the direction that matches your question:

```python
# Monitors that check this endpoint — edges point INTO the endpoint, so direction="in".
incoming = await store.get_edges(endpoint.node_id, direction="in", relation="checks")
rule_ids = [e.src_id for e in incoming]
```

A small helper turns "edges" into "the nodes on the other end", in either direction:

```python
async def follow(store, node_id, relation, direction="out"):
    edges = await store.get_edges(node_id, direction=direction, relation=relation)
    ids   = [e.dst_id if e.src_id == node_id else e.src_id for e in edges]
    return [n for nid in ids if (n := await store.get_node(nid))]

monitors_for_endpoint = await follow(store, endpoint.node_id, relation="checks", direction="in")
endpoints_a_monitor_checks = await follow(store, monitor.node_id, relation="checks", direction="out")
```

**`neighbors` is for outgoing-only walks** filtered by edge *type* (it has no `relation` parameter and follows `direction="out"`). Use it from the "source" end of your relationships:

```python
# Nodes `monitor` points at via any RELATES edge, one hop out.
downstream = await store.neighbors(monitor.node_id, edge_type=EdgeType.RELATES, depth=1)
```

Two sharp edges to know:

- **`depth` is the exact hop distance, not a radius.** `neighbors(..., depth=2)` returns nodes *exactly* two hops out — not the union of hops 1 and 2. On a one-hop graph, `depth=2` returns `[]`. Call it per level if you need each ring.
- **It follows outgoing edges only.** Calling `neighbors` on a node whose domain edges all point *inward* (like `endpoint` above) returns `[]`; reach those with `get_edges(..., direction="in")` / `follow(..., direction="in")` instead.

---

## Richer modeling

**Edge payload & strength.** `Edge.relates` accepts the same kwargs as any edge — use `attributes` for relationship metadata and `weight` for ranking:

```python
Edge.relates(monitor.node_id, endpoint.node_id, relation="checks",
             weight=0.9, attributes={"confidence": 0.9, "source": "import"})
```

**Direction is meaningful.** `relates(A, B, relation="checks")` is `A → B`. Query incoming vs outgoing with `direction="in" | "out" | "both"`. Pick a convention per relation and keep it (e.g. *monitor* → *endpoint* for `checks`) so your filters stay predictable.

**Multiple relations between the same pair** are fine — the store is a multigraph. An SDK method can both `wraps` and (say) `documents` the same endpoint as two separate `RELATES` edges.

**Evolution over time (bi-temporal).** Domain nodes and edges inherit `valid_at` / `invalid_at`. Instead of deleting when a mapping changes, **expire** the old edge so history is preserved and `explain_run` can show *why* a past run behaved as it did:

```python
stale = (await store.get_edges(endpoint.node_id, direction="in", relation="checks"))[0]
await store.upsert_edge(stale.expire())          # soft-retire; invalid_at = now
await store.upsert_edge(Edge.relates(new_monitor_id, endpoint.node_id, relation="checks"))

current = await store.list_edges(relation="checks")               # only_valid=True by default
all_ever = await store.list_edges(relation="checks", only_valid=False)
```

**Multi-tenancy.** Set `group_id` to partition graphs (per project, per tenant, per session). Combine with `domain_type` for narrow scans:

```python
endpoint = ContextNode(name="get_user", domain_type="endpoint", group_id="team_abc")
# later:
await store.list_nodes(domain_type="endpoint", group_id="team_abc")
```

---

## Keeping the two layers clean

- **Don't reuse orchestration edge types for domain links.** An endpoint is not "context for" a monitor via `HAS_CONTEXT`; a monitor `checks` it via `RELATES`. Mixing them makes `ContextNavigator` and retrieval treat your domain edges as agent wiring.
- **Always set `domain_type`** on domain entities. It is the one filter that cleanly separates "things my app models" from "things the runtime executes" — `list_nodes(domain_type=…)` never returns an `AgentNode`.
- **Derive, don't duplicate.** If a domain graph mirrors an existing artifact (a service registry, a database table), treat it as a *projection* you rebuild, not a second source of truth.

---

## Persistence

- **`NetworkXGraphStore`** (default) is in-memory; snapshot with `to_dict()` / `from_dict()`. `domain_type` and `relation` round-trip automatically (they are ordinary model fields).
- **`Neo4jGraphStore`** persists across restarts and supports Cypher traversal. The same filters work: `list_nodes(domain_type=…)` and `get_edges(…, relation=…)` translate to Cypher predicates.

Switching backends requires no change to your domain-modeling code — both implement the same `GraphStore` interface.

---

## Related Docs

- [Your First Graph](first-graph.md) — the orchestration-graph basics this layers onto
- [Explainable Agent Systems](explainable-systems.md) — bi-temporal validity and `explain_run`
- [Graph State Management](graph-state-management.md) — runtime nodes, cleanup, versioning
- [API Reference](../API_REFERENCE.md) — `Node`, `Edge`, `EdgeType`, `GraphStore`
