"""Tests for the domain knowledge-graph extension: Node.domain_type,
Edge.relation / EdgeType.RELATES, and the matching store filters.

These let a consumer layer a typed domain graph (e.g. field / widget /
rule) on top of the orchestration graph without widening the frozen NodeType
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
    """field <-(presents)- widget ; field <-(targets)- rule."""
    field = ContextNode(name="email", domain_type="field")
    widget = ContextNode(name="email_input", domain_type="widget")
    rule = ContextNode(name="require_email", domain_type="rule")
    for n in (field, widget, rule):
        await store.upsert_node(n)
    await store.upsert_edge(Edge.relates(rule.node_id, field.node_id, relation="targets"))
    await store.upsert_edge(Edge.relates(widget.node_id, field.node_id, relation="presents"))
    return store, field, widget, rule


# --- model-level defaults ---------------------------------------------------

def test_domain_fields_default_to_none():
    assert Node().domain_type is None
    assert Edge().relation is None


def test_relates_factory_sets_type_and_label():
    e = Edge.relates("a", "b", relation="targets")
    assert e.edge_type is EdgeType.RELATES
    assert e.relation == "targets"
    assert e.src_id == "a" and e.dst_id == "b"


# --- store filters ----------------------------------------------------------

async def test_list_nodes_filters_by_domain_type(domain_graph):
    store, *_ = domain_graph
    assert [n.name for n in await store.list_nodes(domain_type="field")] == ["email"]
    assert {n.name for n in await store.list_nodes(domain_type="widget")} == {"email_input"}
    assert await store.list_nodes(domain_type="nonexistent") == []
    # absent filter still returns everything
    assert len(await store.list_nodes()) == 3


async def test_list_edges_filters_by_relation(domain_graph):
    store, *_ = domain_graph
    targets = await store.list_edges(relation="targets")
    assert len(targets) == 1 and targets[0].relation == "targets"
    assert all(e.edge_type is EdgeType.RELATES for e in await store.list_edges())


async def test_get_edges_filters_by_relation(domain_graph):
    store, field, widget, rule = domain_graph
    incoming = await store.get_edges(field.node_id, direction="in")
    assert len(incoming) == 2  # both relation edges point at the field
    presents = await store.get_edges(field.node_id, direction="in", relation="presents")
    assert len(presents) == 1 and presents[0].src_id == widget.node_id


async def test_relation_and_edge_type_filters_compose(domain_graph):
    store, field, *_ = domain_graph
    # edge_type filter (existing) and relation filter (new) both apply
    both = await store.get_edges(
        field.node_id, edge_type=EdgeType.RELATES, direction="in", relation="targets"
    )
    assert len(both) == 1 and both[0].relation == "targets"


# --- serialisation round-trip ----------------------------------------------
# NOTE: NetworkXGraphStore.from_dict() spins its own event loop and so cannot
# run inside an async test. We instead exercise the same building blocks it
# uses (model_dump -> node_from_dict / Edge.model_validate), which is what
# carries the new fields across a persisted snapshot.

def test_node_domain_type_survives_serialisation():
    node = ContextNode(name="require_email", domain_type="rule")
    restored = node_from_dict(node.model_dump(mode="json"))
    assert restored.domain_type == "rule"
    assert restored.name == "require_email"


def test_edge_relation_survives_serialisation():
    edge = Edge.relates("a", "b", relation="presents")
    restored = Edge.model_validate(edge.model_dump(mode="json"))
    assert restored.edge_type is EdgeType.RELATES
    assert restored.relation == "presents"


async def test_store_snapshot_includes_domain_fields(domain_graph):
    store, *_ = domain_graph
    snapshot = store.to_dict()
    assert {"rule", "widget", "field"} == {n["domain_type"] for n in snapshot["nodes"]}
    assert {"targets", "presents"} == {e["relation"] for e in snapshot["edges"]}
