"""Tests for the domain knowledge-graph extension: Node.domain_type,
Edge.relation / EdgeType.RELATES, and the matching store filters.

These let a consumer layer a typed domain graph (e.g. endpoint / sdk_method /
monitor) on top of the orchestration graph without widening the frozen NodeType
/ EdgeType enums — yggdrasil itself never interprets these labels.
"""

import pytest

from yggdrasil_lm.core.edges import Edge, EdgeType
from yggdrasil_lm.core.nodes import ContextNode, Node, node_from_dict
from yggdrasil_lm.core.store import NetworkXGraphStore


@pytest.fixture
def store():
    return NetworkXGraphStore()


@pytest.fixture
async def domain_graph(store):
    """endpoint <-(wraps)- sdk_method ; endpoint <-(checks)- monitor."""
    endpoint = ContextNode(name="get_user", domain_type="endpoint")
    sdk_method = ContextNode(name="client.get_user", domain_type="sdk_method")
    monitor = ContextNode(name="get_user_latency", domain_type="monitor")
    for n in (endpoint, sdk_method, monitor):
        await store.upsert_node(n)
    await store.upsert_edge(Edge.relates(monitor.node_id, endpoint.node_id, relation="checks"))
    await store.upsert_edge(Edge.relates(sdk_method.node_id, endpoint.node_id, relation="wraps"))
    return store, endpoint, sdk_method, monitor


# --- model-level defaults ---------------------------------------------------

def test_domain_fields_default_to_none():
    assert Node().domain_type is None
    assert Edge().relation is None


def test_relates_factory_sets_type_and_label():
    e = Edge.relates("a", "b", relation="checks")
    assert e.edge_type is EdgeType.RELATES
    assert e.relation == "checks"
    assert e.src_id == "a" and e.dst_id == "b"


# --- store filters ----------------------------------------------------------

async def test_list_nodes_filters_by_domain_type(domain_graph):
    store, *_ = domain_graph
    assert [n.name for n in await store.list_nodes(domain_type="endpoint")] == ["get_user"]
    assert {n.name for n in await store.list_nodes(domain_type="sdk_method")} == {"client.get_user"}
    assert await store.list_nodes(domain_type="nonexistent") == []
    # absent filter still returns everything
    assert len(await store.list_nodes()) == 3


async def test_list_edges_filters_by_relation(domain_graph):
    store, *_ = domain_graph
    checks = await store.list_edges(relation="checks")
    assert len(checks) == 1 and checks[0].relation == "checks"
    assert all(e.edge_type is EdgeType.RELATES for e in await store.list_edges())


async def test_get_edges_filters_by_relation(domain_graph):
    store, endpoint, sdk_method, _monitor = domain_graph
    incoming = await store.get_edges(endpoint.node_id, direction="in")
    assert len(incoming) == 2  # both relation edges point at the endpoint
    wraps = await store.get_edges(endpoint.node_id, direction="in", relation="wraps")
    assert len(wraps) == 1 and wraps[0].src_id == sdk_method.node_id


async def test_relation_and_edge_type_filters_compose(domain_graph):
    store, endpoint, *_ = domain_graph
    # edge_type filter (existing) and relation filter (new) both apply
    both = await store.get_edges(
        endpoint.node_id, edge_type=EdgeType.RELATES, direction="in", relation="checks"
    )
    assert len(both) == 1 and both[0].relation == "checks"


# --- serialisation round-trip ----------------------------------------------
# NOTE: NetworkXGraphStore.from_dict() spins its own event loop and so cannot
# run inside an async test. We instead exercise the same building blocks it
# uses (model_dump -> node_from_dict / Edge.model_validate), which is what
# carries the new endpoints across a persisted snapshot.

def test_node_domain_type_survives_serialisation():
    node = ContextNode(name="get_user_latency", domain_type="monitor")
    restored = node_from_dict(node.model_dump(mode="json"))
    assert restored.domain_type == "monitor"
    assert restored.name == "get_user_latency"


def test_edge_relation_survives_serialisation():
    edge = Edge.relates("a", "b", relation="wraps")
    restored = Edge.model_validate(edge.model_dump(mode="json"))
    assert restored.edge_type is EdgeType.RELATES
    assert restored.relation == "wraps"


async def test_store_snapshot_includes_domain_fields(domain_graph):
    store, *_ = domain_graph
    snapshot = store.to_dict()
    assert {"monitor", "sdk_method", "endpoint"} == {n["domain_type"] for n in snapshot["nodes"]}
    assert {"checks", "wraps"} == {e["relation"] for e in snapshot["edges"]}
