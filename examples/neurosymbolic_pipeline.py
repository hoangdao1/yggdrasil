"""Neurosymbolic pipeline: neural extraction → symbolic reasoning → neural explanation.

This is the canonical neurosymbolic pattern. The two halves play to their
strengths:

  * **Neural** (``AgentNode``) — reads messy natural language, pulls out
    structured facts, and later turns a verdict back into prose. LLMs are good
    at language; we do NOT trust them to *decide* eligibility.
  * **Symbolic** (``ReasonerNode``) — runs a sound, deterministic Datalog rule
    program over those facts. The decision is verifiable and comes with a proof.

The decision logic lives entirely in rules, so it is auditable and cannot be
hallucinated. The LLM only ever *describes* the rule engine's conclusion.

Run it offline (no API key) with the bundled StubBackend::

    python examples/neurosymbolic_pipeline.py

Swap ``build_app()`` for ``GraphApp()`` to drive the neural steps with a real
model (see examples/subgraph_reuse.py for provider selection).
"""

from __future__ import annotations

import asyncio
import json

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.testing import StubBackend, end_turn


# The rule program — the symbolic core. Edit policy here, not in a prompt.
ELIGIBILITY_RULES = """
    adult(?p)         :- age(?p, ?a), ?a >= 18.
    resident(?p)      :- residency_years(?p, ?y), ?y >= 3.
    good_standing(?p) :- defaults(?p, ?d), ?d = 0.
    sufficient(?p)    :- income(?p, ?i), ?i >= 30000.

    eligible(?p) :- applicant(?p),
                    adult(?p),
                    resident(?p),
                    good_standing(?p),
                    sufficient(?p).

    # A negative conclusion is just as deterministic.
    ineligible(?p) :- applicant(?p), not eligible(?p).
"""


APPLICATION_TEXT = (
    "Applicant Dana Okafor is 34 years old, has lived in-country for 6 years, "
    "earns about $48,000 a year, and has no record of prior loan defaults."
)


def build_app() -> GraphApp:
    """Offline app: stub the two *neural* steps; the symbolic step is real."""
    # 1st chat() call -> extraction agent returns ground facts as JSON.
    # 2nd chat() call -> explanation agent verbalises the verdict.
    extracted = json.dumps(
        [
            ["applicant", "dana"],
            ["age", "dana", 34],
            ["residency_years", "dana", 6],
            ["income", "dana", 48000],
            ["defaults", "dana", 0],
        ]
    )
    explanation = (
        "Dana Okafor is ELIGIBLE. She is over 18, has been resident for more "
        "than 3 years, has no defaults, and earns above the $30,000 floor — so "
        "every clause of the eligibility rule is satisfied."
    )
    return GraphApp(backend=StubBackend([end_turn(extracted), end_turn(explanation)]))


async def main() -> None:
    app = build_app()

    # --- Neural: extract structured facts from free text -------------------
    extractor = await app.add_agent(
        "FactExtractor",
        system_prompt=(
            "Extract loan-application facts as a JSON array of [predicate, ...] "
            "tuples using predicates: applicant, age, residency_years, income, "
            "defaults. Return ONLY the JSON array."
        ),
    )
    ext_ctx = await app.run(extractor, APPLICATION_TEXT)
    facts = json.loads(ext_ctx.outputs[extractor.node_id]["text"])
    print("neural extraction →", facts)

    # --- Symbolic: decide eligibility soundly, with a proof ----------------
    reasoner = await app.add_reasoner(
        "EligibilityReasoner",
        program=ELIGIBILITY_RULES,
        state_keys=["facts"],
        query=["eligible", "ineligible"],
        with_proof=True,
    )
    rea_ctx = await app.run(reasoner, "decide", state={"facts": facts})
    verdict = rea_ctx.outputs[reasoner.node_id]
    print("symbolic verdict →", verdict["facts"])
    for proof in verdict["proofs"]:
        print("   proof:", proof["explanation"])

    is_eligible = any(f["predicate"] == "eligible" for f in verdict["facts"])

    # --- Neural: turn the proven verdict into prose ------------------------
    explainer = await app.add_agent(
        "DecisionExplainer",
        system_prompt="Explain the eligibility decision in plain language for the applicant.",
    )
    decision = "ELIGIBLE" if is_eligible else "INELIGIBLE"
    exp_ctx = await app.run(
        explainer,
        f"Decision: {decision}. Supporting facts: {verdict['facts']}. Explain it.",
    )
    print("\nneural explanation →")
    print(exp_ctx.outputs[explainer.node_id]["text"])


if __name__ == "__main__":
    asyncio.run(main())
