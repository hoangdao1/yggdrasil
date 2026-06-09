"""Unit tests for the Datalog inference engine (the symbolic core)."""

from __future__ import annotations

import pytest

from yggdrasil_lm.symbolic import (
    Program,
    StratificationError,
    UnsafeRuleError,
    fact,
    normalise_fact,
)
from yggdrasil_lm.symbolic.datalog import ParseError, rule_from_obj


def test_transitive_closure():
    prog = Program.parse(
        """
        ancestor(?x, ?y) :- parent(?x, ?y).
        ancestor(?x, ?z) :- parent(?x, ?y), ancestor(?y, ?z).
        """
    )
    sol = prog.solve(
        [fact("parent", "alice", "bob"), fact("parent", "bob", "carol")]
    )
    assert ("ancestor", "alice", "carol") in sol.facts
    assert ("ancestor", "alice", "bob") in sol.facts
    # 2 parent + 3 ancestor facts derived.
    assert len(sol.query("ancestor")) == 3


def test_base_facts_in_program():
    prog = Program.parse(
        """
        parent("alice", "bob").
        grandparent(?x, ?z) :- parent(?x, ?y), parent(?y, ?z).
        parent("bob", "carol").
        """
    )
    sol = prog.solve()
    assert ("grandparent", "alice", "carol") in sol.facts


def test_comparison_builtins():
    prog = Program.parse("adult(?p) :- person(?p, ?age), ?age >= 18.")
    sol = prog.solve(["person(dan, 30)", "person(eve, 12)"])
    assert ("adult", "dan") in sol.facts
    assert ("adult", "eve") not in sol.facts


def test_stratified_negation():
    prog = Program.parse(
        """
        adult(?p) :- person(?p, ?age), ?age >= 18.
        minor(?p) :- person(?p, ?age), not adult(?p).
        """
    )
    sol = prog.solve(["person(dan, 30)", "person(eve, 12)"])
    assert ("minor", "eve") in sol.facts
    assert ("minor", "dan") not in sol.facts
    # 'minor' sits in a strictly higher stratum than 'adult'.
    assert prog.strata == [{"adult"}, {"minor"}]


def test_recursion_through_negation_rejected():
    with pytest.raises(StratificationError):
        Program.parse("p(?x) :- q(?x), not p(?x).").solve(["q(1)"])


def test_unsafe_head_variable_rejected():
    with pytest.raises(UnsafeRuleError):
        Program.parse("bad(?x, ?y) :- foo(?x).")


def test_unsafe_negation_variable_rejected():
    # ?y appears only inside the negated literal — not range-restricted.
    with pytest.raises(UnsafeRuleError):
        Program.parse("bad(?x) :- foo(?x), not bar(?y).")


def test_proof_trace():
    prog = Program.parse(
        """
        ancestor(?x, ?y) :- parent(?x, ?y).
        ancestor(?x, ?z) :- parent(?x, ?y), ancestor(?y, ?z).
        """
    )
    sol = prog.solve(
        [fact("parent", "a", "b"), fact("parent", "b", "c")], with_proof=True
    )
    target = ("ancestor", "a", "c")
    assert target in sol.justifications
    rule_repr, support = sol.justifications[target]
    assert ("parent", "a", "b") in support
    assert "rule:" in sol.explain(target)


def test_derived_excludes_input_facts():
    prog = Program.parse("q(?x) :- p(?x).")
    sol = prog.solve([fact("p", 1)])
    assert ("p", 1) in sol.facts
    assert ("p", 1) not in sol.derived
    assert ("q", 1) in sol.derived


def test_numeric_and_string_constants():
    prog = Program.parse('flag("on") :- count(?n), ?n > 3.')
    sol = prog.solve([fact("count", 5)])
    assert ("flag", "on") in sol.facts


def test_normalise_fact_forms():
    assert normalise_fact(("p", "a", 1)) == ("p", "a", 1)
    assert normalise_fact(["p", "a", 1]) == ("p", "a", 1)
    assert normalise_fact({"predicate": "p", "args": ["a", 1]}) == ("p", "a", 1)
    assert normalise_fact('p(a, 1)') == ("p", "a", 1)


def test_normalise_fact_rejects_variables():
    with pytest.raises(UnsafeRuleError):
        normalise_fact("p(?x)")


def test_rule_from_obj_dict():
    rules = rule_from_obj(
        {"head": "ancestor(?x, ?z)", "body": ["parent(?x, ?y)", "ancestor(?y, ?z)"]}
    )
    assert len(rules) == 1
    assert rules[0].head.predicate == "ancestor"
    assert len(rules[0].body) == 2


def test_zero_arity_atom():
    prog = Program.parse("ready() :- step_done().")
    sol = prog.solve(["step_done()"])
    assert ("ready",) in sol.facts


def test_negation_as_failure_default_closed_world():
    prog = Program.parse("safe(?x) :- node(?x), not flagged(?x).")
    sol = prog.solve(["node(a)", "node(b)", "flagged(b)"])
    assert ("safe", "a") in sol.facts
    assert ("safe", "b") not in sol.facts


def test_malformed_atom_raises():
    with pytest.raises(ParseError):
        Program.parse("this is not datalog")
