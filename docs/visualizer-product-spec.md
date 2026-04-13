---
title: Visualizer Product Spec
parent: Docs
nav_order: 16
---

# Visualizer Product Spec

## Goal

Make the Yggdrasil browser visualizer usable as:

- a fast debugging surface for engineers
- an explainability surface for product and workflow reviewers
- an operations surface for paused, retried, approval-driven, and scheduled workflows

The current UI already exposes trace and graph data, but users still have to manually interpret too much of the run. The improved UI should help users move from raw events to answers.

## Primary User Modes

### 1. Debug Mode

User:

- framework developer
- application engineer
- agent workflow builder

Needs:

- inspect raw payloads
- understand event parent/child relationships
- search and filter large traces quickly
- copy exact event JSON and payloads
- identify failures and low-confidence routes fast

### 2. Explain Mode

User:

- product owner
- reviewer
- workflow designer

Needs:

- plain-English summary of what happened
- why a route was chosen
- which context was selected
- which tools ran and whether they failed
- what happened next after a key decision

### 3. Operations Mode

User:

- operator
- incident responder
- workflow orchestrator

Needs:

- see paused workflows immediately
- inspect approvals, schedules, and checkpoints
- identify permission failures, retries, and resumptions
- understand whether work is waiting for external input
- inspect runtime graph state and coordination primitives

## Product Principles

1. Lead with answers, not raw logs.
2. Keep raw payloads one click away.
3. Make operational states visually loud.
4. Preserve shareability and reproducibility.
5. Keep the visualizer self-hosted and local-first.

## UX Requirements

### Information Architecture

The UI should provide four top-level views:

- `Summary`: run outcome, risks, latest state, and critical counts
- `Events`: searchable and filterable event stream
- `Detail`: deep inspection of the selected event
- `Stats`: aggregate trace metrics

The store/database view remains separate and should still be accessible.

### Triage Controls

The event stream must support:

- free-text search
- event-type filtering
- `errors only`
- `runtime only`
- `chronological` vs `group by hop`

### Event Navigation

The UI must support:

- selecting an event from the list
- selecting a node from the graph
- jumping to parent event
- jumping to direct child events
- seeing related events for the same node

### Workflow-Runtime Support

The UI must provide first-class presentation for:

- `pause`
- `resume`
- `retry`
- `validation`
- `permission_denied`
- `checkpoint`
- `approval_task`
- `lease`
- `schedule`
- `migration`

These should not depend on the raw payload accordion for basic understanding.

### Graph Interaction

The trace graph should support:

- fit to screen
- reset zoom
- highlight the selected node
- center on selected node
- optional path emphasis through related nodes

The database/store graph should support:

- lazy loading for large graphs
- stable selection
- legend
- fit/reset controls

## Server And Message Model

The visualizer server should emit a lightweight UI-oriented summary model in addition to raw events.

### Message Types

- `meta`
- `event`
- `graph_state`
- `summary`
- `finalize`

### Summary Shape

The summary payload should include:

- `status`
- `finalized`
- `session_id`
- `query`
- `current_node_id`
- `current_node_name`
- `selected_event_id`
- event counts by type
- error count
- warning count
- low-confidence route count
- pause count
- approval count
- checkpoint count
- schedule count
- latest pause
- latest approval task
- latest permission failure

The browser should use this model for the Summary tab and status bar rather than recomputing every high-level interpretation from scratch.

## DevEx Requirements

1. The UI code should be split into separate static files instead of one large inline HTML document.
2. Static assets should be served by the FastAPI app under `/static`.
3. The server should keep backward-compatible websocket behavior for existing tests and integrations.
4. Visualizer behavior should be testable from fixture traces and server unit tests.

## Release Slices

### Slice 1

- static asset split
- summary model from server
- Summary tab
- triage controls
- richer runtime event rendering

### Slice 2

- parent/child navigation
- copy helpers
- improved graph interactions
- better loading and disconnected states

### Slice 3

- fixture-driven UI regression coverage
- narrative explain mode
- deeper compare and workflow-operations features

## Non-Goals For This Pass

- multi-run comparison UI
- cloud hosting or auth
- distributed scheduler guarantees
- external inbox or notification delivery
