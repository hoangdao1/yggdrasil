---
title: Core Runtime Maturity
parent: Docs
nav_order: 14
---

# Core Runtime Maturity

This note tracks the maturity of the workflow-runtime features that were promoted into the core engine.

## Summary

The current implementation provides usable v1 primitives for all of the capabilities below.

That means:

- the core now has real support for these areas
- several features are ready for prototypes and serious internal pilots
- some areas still need deeper hardening before they should be treated as enterprise-complete

## Maturity Table

| Capability | Implemented | Usable Now | Current Scope | Main Gaps / Next Upgrade |
|---|---|---|---|---|
| Stronger schema / constraint enforcement during execution | Yes | Yes | Tool input/output validation, workflow-state validation, `VALIDATES`-linked schema checks, `ConstraintRule` invariants | Constraint language is intentionally compact; no visual policy editor or full declarative rule authoring UX |
| First-class human-in-the-loop / approval pause-resume nodes | Yes | Yes | `pause_before`, `pause_after`, `wait_for_input`, `ApprovalNode`, inbox tasks, assignees, SLA/escalation metadata, checkpoints, restore | No external inbox UI, notification delivery, or multi-party approval quorum model |
| Better durable state and long-running workflow semantics | Yes | Yes | `ExecutionContext.state`, checkpoint nodes, resume APIs | Single-process by default; no distributed worker fleet management or external scheduler integration |
| Stronger deterministic routing and guardrails for business-critical flows | Yes | Yes | `RouteRule` evaluation before LLM routing, decision tables, routing trace mode distinction | No hosted rule editor or formal proof system for route completeness/conflict analysis |
| Versioning / migration for workflow graphs | Partial | Yes | `graph_version` on nodes for semantic compatibility | No migration hook or dry-run diff UI |
| Support for transactional steps, retries, and idempotency | Yes | Yes | Execution policies, retry/backoff/timeout, idempotency key on tools | Idempotency is in-memory only; no external coordination |

## Practical Read

For product planning, the safest interpretation is:

- schema validation, deterministic routing, retries, and pause/resume are real core features now
- durable state, migrations, and retries are usable core features
- schema validation, deterministic routing, and pause/resume are solid

## Recommended Next Upgrades

If the project moves toward production business workflows, the highest-value follow-up work is:

1. External scheduler and worker fleet integration for long-running workflows
2. Rule authoring UX and stronger routing verification tooling
3. Migration diffing / operator workflows
