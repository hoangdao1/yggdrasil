// Status bar + connection badge + graph empty state.

import { state, selectCounts } from "./state.js";

export function updateConnectionBadge() {
  const badge = document.getElementById("conn-badge");
  if (!badge) return;
  if (state.connectionState === "live") {
    badge.className = "badge badge-live";
    badge.textContent = "Live";
  } else if (state.connectionState === "reconnecting") {
    badge.className = "badge badge-conn";
    badge.textContent = "Reconnecting";
  } else if (state.connectionState === "error") {
    badge.className = "badge badge-error";
    badge.textContent = "Error";
  } else if (state.connectionState === "done") {
    badge.className = "badge badge-done";
    badge.textContent = "Done";
  } else {
    badge.className = "badge badge-conn";
    badge.textContent = "Connecting";
  }
}

export function updateStatusBar() {
  const summary = state.summary || {};
  const counts = selectCounts();
  const toolCalls = counts.tool_call || 0;
  const agents = counts.agent_start || 0;
  const hops = counts.hop || 0;
  const warnings = summary.warning_count || 0;
  const errors = summary.error_count || 0;

  setText("stat-hops", `${hops} hops`);
  setText("stat-events", `${summary.event_count || state.events.length} events`);
  setText("stat-agents", `${agents} agents`);
  setText("stat-tools", `${toolCalls} tool calls`);
  setText("stat-errors", `${errors} errors`);
  setText("stat-warnings", `${warnings} warnings`);

  const runBadge = document.getElementById("run-status-badge");
  if (runBadge) {
    const status = summary.status || (state.finalized ? "completed" : "waiting");
    runBadge.textContent = status.replaceAll("_", " ");
    runBadge.className = "badge";
    if (status === "paused") runBadge.classList.add("badge-paused");
    else if (status === "error" || errors > 0 || status === "completed_with_issues") runBadge.classList.add("badge-error");
    else if (status === "completed") runBadge.classList.add("badge-done");
    else runBadge.classList.add("badge-live");
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

export function updateGraphEmptyState() {
  const emptyMessage = document.getElementById("graph-empty-message");
  if (!emptyMessage) return;
  if (state.connectionState === "connecting") emptyMessage.textContent = "Connecting to the local visualizer server.";
  else if (state.connectionState === "reconnecting") emptyMessage.textContent = "Connection dropped. Retrying websocket connection.";
  else if (state.summary?.status === "paused") emptyMessage.textContent = "Workflow is paused and waiting for external input or approval.";
  else if (state.traceNodes.size === 0) emptyMessage.textContent = "Run your graph and trace events will stream in real time.";
  else emptyMessage.textContent = "Use the graph controls to inspect the trace.";
}
