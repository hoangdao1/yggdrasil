"""Integration tests for ReasonerNode — the symbolic step inside a graph."""

from __future__ import annotations

import json

import pytest

from yggdrasil_lm import GraphApp
from yggdrasil_lm.core.edges import Edge, EdgeType
from yggdrasil_lm.testing import StubBackend, end_turn


@pytest.mark.asyncio
async def test_reasoner_from_state_facts():
    app = GraphApp(backend=StubBackend([end_turn("ok")]))
    reasoner = await app.add_reasoner(
        "Ancestors",
        program="""
            ancestor(?x, ?y) :- parent(?x, ?y).
            ancestor(?x, ?z) :- parent(?x, ?y), ancestor(?y, ?z).
        """,
        state_keys=["kin"],
        query=["ancestor"],
        with_proof=True,
    )
    ctx = await app.run(
        reasoner,
        "go",
        state={"kin": [["parent", "a", "b"], ["parent", "b", "c"]]},
    )
    out = ctx.outputs[reasoner.node_id]
    preds = {(f["predicate"], tuple(f["args"])) for f in out["facts"]}
    assert ("ancestor", ("a", "c")) in preds
    assert out["fact_count"] == 3
    assert out["proofs"]  # proof recorded
    # Output also written to state under output_key.
    assert ctx.state.data["inferred"]["fact_count"] == 3


@pytest.mark.asyncio
async def test_reasoner_reads_kg_edges_as_facts():
    app = GraphApp(backend=StubBackend([end_turn("ok")]))
    doc = await app.add_context("DocA", "x")
    e1 = await app.add_context("Entity1", "y")
    e2 = await app.add_context("Entity2", "z")
    await app.store.upsert_edge(
        Edge(edge_type=EdgeType.MENTIONS, src_id=doc.node_id, dst_id=e1.node_id)
    )
    await app.store.upsert_edge(
        Edge(edge_type=EdgeType.SIMILAR_TO, src_id=e1.node_id, dst_id=e2.node_id)
    )
    reasoner = await app.add_reasoner(
        "Relate",
        program="""
            related(?x, ?y) :- mentions(?x, ?y).
            related(?x, ?z) :- mentions(?x, ?y), similar_to(?y, ?z).
        """,
        edge_types=["MENTIONS", "SIMILAR_TO"],
        query=["related"],
    )
    ctx = await app.run(reasoner, "go")
    pairs = {tuple(f["args"]) for f in ctx.outputs[reasoner.node_id]["facts"]}
    assert ("DocA", "Entity1") in pairs
    assert ("DocA", "Entity2") in pairs  # transitive via similar_to


@pytest.mark.asyncio
async def test_reasoner_fail_on_empty():
    app = GraphApp(backend=StubBackend([end_turn("ok")]))
    reasoner = await app.add_reasoner(
        "MustDerive",
        program="eligible(?p) :- applicant(?p), adult(?p).",
        state_keys=["facts"],
        query=["eligible"],
        fail_on_empty=True,
    )
    with pytest.raises(RuntimeError):
        await app.run(reasoner, "go", state={"facts": [["applicant", "x"]]})


@pytest.mark.asyncio
async def test_neurosymbolic_extract_reason_loop():
    """Neural extraction (stubbed) feeds the symbolic reasoner."""
    extracted = json.dumps(
        [["applicant", "dana"], ["age", "dana", 34], ["income", "dana", 48000]]
    )
    app = GraphApp(backend=StubBackend([end_turn(extracted)]))
    extractor = await app.add_agent("Extractor", system_prompt="extract facts")
    ext_ctx = await app.run(extractor, "Dana is 34 earning 48000")
    facts = json.loads(ext_ctx.outputs[extractor.node_id]["text"])

    reasoner = await app.add_reasoner(
        "Eligibility",
        program="""
            adult(?p)      :- age(?p, ?a), ?a >= 18.
            sufficient(?p) :- income(?p, ?i), ?i >= 30000.
            eligible(?p)   :- applicant(?p), adult(?p), sufficient(?p).
        """,
        state_keys=["facts"],
        query=["eligible"],
    )
    ctx = await app.run(reasoner, "decide", state={"facts": facts})
    eligible = [f for f in ctx.outputs[reasoner.node_id]["facts"] if f["predicate"] == "eligible"]
    assert eligible and eligible[0]["args"] == ["dana"]


@pytest.mark.asyncio
async def test_reasoner_dict_rules():
    app = GraphApp(backend=StubBackend([end_turn("ok")]))
    reasoner = await app.add_reasoner(
        "DictRules",
        rules=[
            {"head": "grandparent(?x, ?z)", "body": ["parent(?x, ?y)", "parent(?y, ?z)"]},
        ],
        state_keys=["facts"],
        query=["grandparent"],
    )
    ctx = await app.run(
        reasoner, "go", state={"facts": [["parent", "a", "b"], ["parent", "b", "c"]]}
    )
    pairs = {tuple(f["args"]) for f in ctx.outputs[reasoner.node_id]["facts"]}
    assert ("a", "c") in pairs
