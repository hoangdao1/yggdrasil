# Neurosymbolic Reasoning

Yggdrasil pairs the **neural** half of an agent system — an `AgentNode` (an LLM)
that reads messy natural language — with a **symbolic** half: a `ReasonerNode`
backed by a built-in, dependency-free Datalog engine. The agent handles
language; the reasoner makes the *decision* soundly, deterministically, and with
a proof — so the verdict can't be hallucinated.

The canonical loop is **extract → reason → explain**: the LLM turns text into
ground facts, Datalog derives the decision with a proof, and the LLM turns that
proof back into prose. See `examples/neurosymbolic_pipeline.py` for a runnable
end-to-end demo (offline, no API key).

## How `ReasonerNode` works

A `ReasonerNode` (node type `REASONER`, defined in `yggdrasil_lm/core/nodes.py`)
runs an inference program over ground facts and writes the derived facts back —
with **no LLM call**. Like `TransformNode`, the executor runs it inline.

```python
reasoner = await app.add_reasoner(
    "EligibilityReasoner",
    program="""
        adult(?p)      :- age(?p, ?a), ?a >= 18.
        sufficient(?p) :- income(?p, ?i), ?i >= 30000.
        eligible(?p)   :- applicant(?p), adult(?p), sufficient(?p).
    """,
    state_keys=["facts"],     # facts an upstream agent extracted into state
    edge_types=["MENTIONS"],  # AND/OR knowledge-graph edges as binary facts
    query=["eligible"],       # predicates to surface (empty = all derived)
    with_proof=True,          # attach a justification per derived fact
    output_key="inferred",    # also written to ctx.state.data["inferred"]
)
ctx = await app.run(reasoner, "decide", state={"facts": [
    ["applicant", "dana"], ["age", "dana", 34], ["income", "dana", 48000],
]})
ctx.outputs[reasoner.node_id]["facts"]   # [{"predicate": "eligible", "args": ["dana"]}]
```

The execution lifecycle (`GraphExecutor._execute_reasoner`):

1. **Compile the program.** `program` (string DSL) and `rules` (structured
   dicts) are parsed and handed to `Program(...)`, which **validates and
   stratifies** at construction time — unsafe rules and recursion-through-
   negation are rejected here, before any facts are touched.
2. **Gather facts** (the neural→symbolic bridge). Facts come from up to three
   sources, controlled by `FactSource`:
   - `state_keys` — fact lists an upstream agent wrote into `ctx.state.data`.
   - `edge_types` — knowledge-graph edges loaded as binary facts: a `MENTIONS`
     edge becomes `mentions(src, dst)`, turning the typed graph into a fact base.
   - `include_node_facts` — each node becomes a unary fact `node_type(name)`.

   Facts may be tuples, `{"predicate", "args"}` dicts, `["pred", ...]` lists, or
   atom-syntax strings; `normalise_fact` coerces them.
3. **Solve.** `program.solve(...)` runs in a worker thread under the node's
   retry/timeout policy and computes the **deductive closure**.
4. **Project.** Keep `derived` facts (or all, if `emit_derived_only=False`),
   filtered to the `query` predicates. `fail_on_empty` raises if nothing was
   derived — useful as a guard.
5. **Write back.** The result dict is written to `ctx.state.data[output_key]`
   for a downstream agent, and a trace event is emitted.

Output shape:

```python
{
  "facts": [{"predicate": "eligible", "args": ["dana"]}],
  "fact_count": 1,
  "input_count": 3,
  "predicates": ["eligible"],
  "proofs": [{"fact": {...}, "explanation": "eligible('dana') ⟸ applicant('dana'), adult('dana'), sufficient('dana')  [rule: ...]"}],
}
```

The `proofs` (when `with_proof=True`) are the explainability hook: each derived
fact records the rule and the exact ground premises that justified it. The LLM
downstream only *describes* a conclusion the rule engine *proved*.

## Why Datalog instead of a plain Python function?

Yggdrasil already has `TransformNode` for "just run a Python callable." So why
reach for a rule engine? They are complementary, but Datalog wins decisively for
one shape of problem: **relational, recursive, declarative decision logic that
needs to be auditable.**

### The concrete contrast

Take "who is an ancestor of whom." In Datalog:

```
ancestor(?x, ?y) :- parent(?x, ?y).
ancestor(?x, ?z) :- parent(?x, ?y), ancestor(?y, ?z).
```

The equivalent Python function:

```python
def ancestors(parent_facts):
    edges = defaultdict(set)
    for _, p, c in parent_facts:
        edges[p].add(c)
    result, frontier = set(), set(...)
    while frontier:          # you write the worklist
        ...                  # you handle the fixpoint
        ...                  # you guard against cycles / non-termination
    return result
```

You've now hand-written graph traversal, a termination guard, and a join — the
plumbing the engine gives you for free. Datalog says **what** holds; the engine
figures out **how** to derive it.

### Where Datalog pulls ahead

1. **Recursion / transitive closure is free and guaranteed to terminate.**
   Reachability, ancestry, dependency chains, "can A influence B through any
   path" are one-line rules. Pure Datalog is decidable: the closure is finite
   and the fixpoint always halts. A Python loop can spin forever or miss a cycle
   guard.

2. **It's declarative and order-independent.** Rules state relationships. Adding
   a case is *adding a rule* — you never touch the others, and rule order does
   not matter. In a Python function, adding a case means editing control flow,
   and the order of `if`s and intermediate variables is load-bearing.

3. **Built-in provenance — the killer feature here.** With `with_proof=True` the
   engine records *why* each fact holds:
   `eligible('dana') ⟸ applicant('dana'), adult('dana'), resident('dana'), sufficient('dana')`.
   A Python function returns `True` and leaves you to reconstruct the reasoning
   with manual logging. For a system whose point is *verifiable,
   non-hallucinated decisions*, the proof tree is the deliverable.

4. **Static guarantees before it runs.** `Program(...)` validates **safety**
   (every variable range-restricted) and **stratification** (no recursion
   through negation) at compile time. A whole class of bugs is caught
   structurally; Python finds them at runtime, if at all.

5. **Purity and analyzability.** A `ReasonerNode` is guaranteed to have no side
   effects, no network, no infinite loop, no mutated global. You can reason
   *about* it. A Python function can do anything — which is exactly why you
   cannot trust it as an auditable policy.

6. **One uniform fact base across sources.** Facts from LLM extraction,
   knowledge-graph edges, and workflow state all land in the same relation
   space, and rules join across them transparently. A function would have to
   manually reconcile those shapes.

7. **Rules are data, not code.** The program is a string — it can be stored as a
   node, versioned, hot-swapped, reviewed by a non-engineer ("policy lives here,
   in plain rules"), or even generated by an LLM. Changing a Python function
   means a code deploy.

### When a plain function is genuinely better

Reach for `TransformNode` (a Python callable, no LLM) instead when the work is:

- **Numeric / aggregation-heavy** — sums, averages, scoring, date math. Datalog
  is relational, not arithmetic.
- **String / format reshaping** — parsing, templating, serialization.
- **One-shot and non-recursive** — a single deterministic transform with no rule
  interaction.
- **Performance-critical on large data** — the built-in engine is a naive
  fixpoint evaluator, not an optimized Datalog system.

### Rule of thumb

> If the logic is *relational* ("X holds when Y and Z relate this way"),
> *recursive*, or needs to be *audited / edited as policy* → `ReasonerNode`
> (Datalog). If it's *procedural* number-crunching or reshaping →
> `TransformNode` (Python).

The neurosymbolic payoff is the combination: the LLM turns language into facts,
Datalog derives the decision soundly and with a proof, and the LLM turns that
proof back into prose. The middle step is precisely the one you do not want a
hand-written function — or an LLM — to be trusted with.

## The Datalog DSL in brief

- Variables are `?x`; constants are `"quoted"`, numbers, `true`/`false`, or bare
  words. Atoms are `predicate(term, ...)`; a fact is a rule with an empty body.
- Rules: `head :- body1, body2.` (trailing `.` optional). Comments start with
  `#` or `%`.
- **Comparison built-ins** in bodies: `=` `==` `!=` `<` `<=` `>` `>=`
  (e.g. `adult(?p) :- person(?p, ?age), ?age >= 18`).
- **Negation as failure** with stratification: `safe(?x) :- node(?x), not flagged(?x)`.
- Unsafe rules (unbound head/negation/comparison variables) and
  recursion-through-negation are rejected at compile time.

The engine is also usable standalone, independent of the graph:

```python
from yggdrasil_lm.symbolic import Program, fact

prog = Program.parse("""
    ancestor(?x, ?y) :- parent(?x, ?y).
    ancestor(?x, ?z) :- parent(?x, ?y), ancestor(?y, ?z).
""")
sol = prog.solve([fact("parent", "alice", "bob"), fact("parent", "bob", "carol")], with_proof=True)
sol.query("ancestor")               # all ancestor facts
sol.explain(("ancestor", "alice", "carol"))  # one-line justification
```

See `yggdrasil_lm/symbolic/datalog.py` for the full engine and
`examples/neurosymbolic_pipeline.py` for the extract → reason → explain pattern.
