# Control Plane Thesis

`yggdrasil` is most useful when your agent system changes over time.

That means:

- tools change
- context changes
- routing changes
- policies change
- workflow steps change
- operators need to understand why the system behaved a certain way

## The Core Idea

Most agent frameworks treat orchestration as application code.

`yggdrasil` treats orchestration as a graph that can be:

- stored
- versioned
- explained
- inspected after execution

That makes it a better fit for agent systems that behave more like operational systems than prompt demos.

## Why This Matters

If the agent system changes over time, teams need answers to questions like:

- which tools did this agent have at runtime?
- why was this context selected?
- what route caused this request to move to another agent?
- what changed between last week and this week?
- which graph edit changed behavior?

`yggdrasil` is built to make those questions answerable.

## What Makes The Project Different

### 1. The graph is the control surface

Agents, tools, prompts, context, approvals, and runtime artifacts can live in the same graph model.

### 2. Runtime composition is explainable

The system can explain:

- which tools were attached
- which context was selected
- what ranked higher or lower
- which route fired

### 3. Change is part of the product

Graph versioning, checkpoints, and structured traces are not side features. They are part of managing an evolving agent system safely.

### 4. Observability is tied to control-plane questions

Tracing is useful not only for debugging latency or failures, but for answering:

- why did the system behave this way?
- what composition was active?
- what changed?

## Best-Fit Use Cases

- internal copilots with changing policies and capabilities
- approval-heavy enterprise workflows
- multi-agent systems with tenant- or role-specific behavior
- operational agent systems that require review, migration, and explainability
