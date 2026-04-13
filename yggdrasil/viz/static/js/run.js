// Combined Run tab: banner → callouts → stats → per-agent/tool breakdown → explain narrative.

import { state, selectCounts, selectAgentNames, selectToolNames, selectNodeStats } from "./state.js";
import {
  escapeHtml,
  eventLabel,
  eventTypeClass,
  isErrorEvent,
  RUNTIME_EVENT_TYPES,
  fmtDurationMs,
} from "./format.js";
import { eventSummary } from "./event-summary.js";
import { nodeNameForId } from "./state.js";

export async function fetchExplain() {
  if (state.explainLoading) return;
  state.explainLoading = true;
  renderRunTab();
  try {
    const sessionId = state.meta?.session_id || "";
    const resp = await fetch("/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
    state.explain = resp.ok ? await resp.json() : null;
  } catch (_) {
    state.explain = null;
  } finally {
    state.explainLoading = false;
    renderRunTab();
  }
}

export function renderRunTab() {
  const container = document.getElementById("tab-run");
  if (!container) return;
  const summary = state.summary;

  if (!summary) {
    container.innerHTML = "<div class='empty-panel'>Waiting for trace data…</div>";
    return;
  }

  let html = "";
  html += renderBanner(summary);
  html += renderCallouts(summary);
  html += renderStatGrid(summary);
  html += renderWorkflowState(summary);
  html += renderNodeBreakdown();
  html += renderRuntimeChips();
  html += renderExplainNarrative();

  container.innerHTML = html;

  container.querySelectorAll(".error-list-item[data-event-id]").forEach((el) => {
    el.addEventListener("click", () => {
      window.dispatchEvent(new CustomEvent("viz:select-event", { detail: { eventId: el.dataset.eventId } }));
    });
  });
  container.querySelector("#explain-copy-btn")?.addEventListener("click", () => {
    if (state.explain && navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(JSON.stringify(state.explain, null, 2)).catch(() => {});
    }
  });
}

function renderBanner(summary) {
  const title = escapeHtml((summary.status || "waiting").replaceAll("_", " "));
  const q = escapeHtml(summary.query || state.meta?.query || "Waiting for query");
  const latest = summary.current_node_name
    ? ` · latest node: ${escapeHtml(summary.current_node_name)}`
    : "";
  return `
    <div class="summary-banner">
      <div class="summary-title">${title}</div>
      <div class="summary-subtitle">${q}${latest}</div>
    </div>
  `;
}

function renderCallouts(summary) {
  const callouts = [];
  if (summary.fatal_error_count > 0) {
    const fatalEvents = state.events.filter((e) => e.event_type === "error");
    const items = fatalEvents.map((e) =>
      `<div class="error-list-item" data-event-id="${e.event_id}">` +
      `<span class="error-list-type ${eventTypeClass(e.event_type)}">${eventLabel(e.event_type)}</span>` +
      `<span class="error-list-node">${escapeHtml((e.payload || {}).error_type || "Error")}</span>` +
      `<span class="error-list-msg">${escapeHtml((e.payload || {}).error || "")}</span>` +
      `</div>`
    ).join("");
    callouts.push(`<div class="callout error"><strong>Executor crashed with an unhandled exception.</strong>${items}</div>`);
  } else if (summary.error_count > 0) {
    const errorEvents = state.events.filter(isErrorEvent);
    const items = errorEvents.map((e) =>
      `<div class="error-list-item" data-event-id="${e.event_id}">` +
      `<span class="error-list-type ${eventTypeClass(e.event_type)}">${eventLabel(e.event_type)}</span>` +
      `<span class="error-list-node">${escapeHtml(e.node_name || e.node_id)}</span>` +
      `<span class="error-list-msg">${escapeHtml(eventSummary(e))}</span>` +
      `</div>`
    ).join("");
    callouts.push(`<div class="callout error"><strong>${summary.error_count} error${summary.error_count !== 1 ? "s" : ""} detected.</strong>${items}</div>`);
  }
  if (summary.warning_count > 0) {
    callouts.push(`<div class="callout warning"><strong>${summary.warning_count} low-confidence routes.</strong><div class="summary-subtitle">Review routing decisions with confidence below 70% before trusting the result.</div></div>`);
  }
  if (summary.status === "paused" && summary.latest_pause) {
    callouts.push(`<div class="callout info"><strong>Workflow is paused.</strong><div class="summary-subtitle">${escapeHtml(eventSummary(summary.latest_pause))}</div></div>`);
  }
  if (summary.latest_approval_task) {
    callouts.push(`<div class="callout info"><strong>Approval task created.</strong><div class="summary-subtitle">${escapeHtml(eventSummary(summary.latest_approval_task))}</div></div>`);
  }
  if (!callouts.length) {
    callouts.push(`<div class="callout info"><strong>No obvious operational blockers.</strong><div class="summary-subtitle">Use the Events tab to inspect the full run.</div></div>`);
  }
  return `<div class="summary-callouts">${callouts.join("")}</div>`;
}

function renderStatGrid(summary) {
  const counts = selectCounts();
  return `
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-val">${summary.event_count || state.events.length}</div><div class="stat-label">Events</div></div>
      <div class="stat-card"><div class="stat-val">${counts.hop || 0}</div><div class="stat-label">Hops</div></div>
      <div class="stat-card"><div class="stat-val">${counts.tool_call || 0}</div><div class="stat-label">Tool calls</div></div>
      <div class="stat-card"><div class="stat-val">${counts.agent_start || 0}</div><div class="stat-label">Agents</div></div>
      <div class="stat-card"><div class="stat-val">${summary.error_count || 0}</div><div class="stat-label">Errors</div></div>
      <div class="stat-card"><div class="stat-val">${summary.warning_count || 0}</div><div class="stat-label">Warnings</div></div>
      <div class="stat-card"><div class="stat-val">${summary.pause_count || 0}</div><div class="stat-label">Pauses</div></div>
      <div class="stat-card"><div class="stat-val">${summary.approval_count || 0}</div><div class="stat-label">Approvals</div></div>
    </div>
  `;
}

function renderWorkflowState(summary) {
  return `
    <div class="section-title">Latest workflow state</div>
    <div class="detail-section">
      <div class="kv-row"><span class="kv-key">session</span><span class="kv-val">${escapeHtml((summary.session_id || "").slice(0, 8))}</span></div>
      <div class="kv-row"><span class="kv-key">current node</span><span class="kv-val">${escapeHtml(summary.current_node_name || "n/a")}</span></div>
      <div class="kv-row"><span class="kv-key">finalized</span><span class="kv-val">${summary.finalized ? "yes" : "no"}</span></div>
      <div class="kv-row"><span class="kv-key">runtime events</span><span class="kv-val">${summary.runtime_event_count || 0}</span></div>
    </div>
  `;
}

function renderNodeBreakdown() {
  const agentNames = selectAgentNames();
  const toolNames = selectToolNames();
  const stats = selectNodeStats();

  // Join agent/tool names to per-node stats.
  const rowsFor = (names, kind) => {
    if (!names.length) return `<div class="empty-panel">none</div>`;
    return names.map((name) => {
      // Find the node id(s) matching this name — use first matching entry.
      let match = null;
      for (const n of state.traceNodes.values()) {
        if (n.name === name) { match = n; break; }
      }
      const s = match ? stats.get(match.refNodeId || match.id) : null;
      const parts = [];
      if (s?.toolCalls) parts.push(`${s.toolCalls} calls`);
      if (s?.errors) parts.push(`<span class="log-err">${s.errors} err</span>`);
      if (s?.totalMs) parts.push(fmtDurationMs(s.totalMs));
      const meta = parts.length ? `<span class="breakdown-meta">${parts.join(" · ")}</span>` : "";
      return `<div class="breakdown-row breakdown-${kind}"><span class="chip chip-${kind}">${escapeHtml(name)}</span>${meta}</div>`;
    }).join("");
  };

  return `
    <div class="section-title">Agents</div>
    <div class="breakdown-list">${rowsFor(agentNames, "agent")}</div>
    <div class="section-title">Tools used</div>
    <div class="breakdown-list">${rowsFor(toolNames, "tool")}</div>
  `;
}

function renderRuntimeChips() {
  const counts = selectCounts();
  const chips = [...RUNTIME_EVENT_TYPES].map((type) =>
    `<span class="chip chip-runtime">${escapeHtml(eventLabel(type))} · ${counts[type] || 0}</span>`
  ).join("");
  return `
    <div class="section-title">Runtime events</div>
    <div>${chips}</div>
  `;
}

function renderExplainNarrative() {
  if (state.explainLoading) {
    return `<div class="section-title">Run explanation</div><div class="empty-panel">Loading explanation…</div>`;
  }
  if (!state.explain) {
    return `<div class="section-title">Run explanation</div><details class="explain-details"><summary>Not available yet — appears once the run is finalized.</summary></details>`;
  }
  const ex = state.explain;
  const s = ex.summary || {};
  const graph = ex.graph || {};

  let out = `<div class="section-title">Run explanation</div>`;
  out += `<details class="explain-details" open>`;
  out += `<summary>Narrative breakdown (${ex.hops?.length || 0} hops)</summary>`;

  out += `<div class="stat-grid" style="margin-top:8px">
    <div class="stat-card"><div class="stat-val">${ex.hop_count || 0}</div><div class="stat-label">Hops</div></div>
    <div class="stat-card"><div class="stat-val">${s.routing_decision_count || 0}</div><div class="stat-label">Routing</div></div>
    <div class="stat-card"><div class="stat-val">${s.tool_call_count || 0}</div><div class="stat-label">Tool calls</div></div>
    <div class="stat-card"><div class="stat-val">${s.context_injection_count || 0}</div><div class="stat-label">Context</div></div>
  </div>`;

  out += `<div class="section-title">Graph</div><div class="detail-section">
    <div class="kv-row"><span class="kv-key">revision</span><span class="kv-val">${escapeHtml(String(graph.graph_revision_id || "—").slice(0, 16))}</span></div>
    <div class="kv-row"><span class="kv-key">version</span><span class="kv-val">${escapeHtml(graph.graph_version || "v1")}</span></div>
    <div class="kv-row"><span class="kv-key">policy</span><span class="kv-val">${escapeHtml(graph.graph_revision_policy || "warn")}</span></div>
  </div>`;

  if (ex.hops?.length) {
    out += `<div class="section-title">Hops</div>`;
    out += ex.hops.map((hop) => `
      <div class="detail-section" style="padding:8px 10px;margin-bottom:4px">
        <div class="kv-row">
          <span class="kv-key" style="min-width:36px">hop ${hop.hop != null ? hop.hop : "?"}</span>
          <span class="kv-val">${escapeHtml(hop.node_name || hop.node_id)}</span>
        </div>
        ${hop.summary ? `<div class="event-meta" style="margin-top:2px">${escapeHtml(hop.summary)}</div>` : ""}
      </div>
    `).join("");
  }

  if (ex.routing?.length) {
    out += `<div class="section-title">Routing decisions</div>`;
    out += ex.routing.map((r) => {
      const conf = r.confidence != null
        ? `<span class="kv-val" style="color:${r.confidence < 0.7 ? "var(--yellow)" : "var(--green)"}">${(r.confidence * 100).toFixed(0)}%</span>`
        : "";
      const nextName = r.next_node_id ? nodeNameForId(r.next_node_id) : "end";
      return `
        <div class="detail-section" style="padding:8px 10px;margin-bottom:4px">
          <div class="kv-row">
            <span class="kv-key">${escapeHtml(r.node_name || r.node_id)}</span>
            <span class="kv-val">${escapeHtml(r.intent || "default")} → ${escapeHtml(nextName)}</span>
            ${conf}
          </div>
          <div class="event-meta">mode: ${escapeHtml(r.mode || "llm")}</div>
        </div>
      `;
    }).join("");
  }

  if (ex.tool_calls?.length) {
    out += `<div class="section-title">Tool calls</div>`;
    out += ex.tool_calls.map((tc) => {
      const inputStr = JSON.stringify(tc.input || {});
      const preview = inputStr.length > 120 ? `${inputStr.slice(0, 119)}…` : inputStr;
      return `
        <div class="detail-section" style="padding:8px 10px;margin-bottom:4px">
          <div class="kv-row">
            <span class="kv-key">${escapeHtml(tc.tool_name || tc.callable_ref || "tool")}</span>
            <span class="kv-val" style="color:var(--text-dim);font-size:11px">${escapeHtml(tc.callable_ref || "")}</span>
          </div>
          <div class="event-meta">${escapeHtml(preview)}</div>
        </div>
      `;
    }).join("");
  }

  if (ex.pauses?.length) {
    out += `<div class="section-title">Pauses</div>`;
    out += ex.pauses.map((p) => `
      <div class="detail-section" style="padding:8px 10px;margin-bottom:4px">
        <div class="kv-row"><span class="kv-key">${escapeHtml(p.node_name || p.node_id)}</span><span class="kv-val">${escapeHtml(p.reason || "paused")}</span></div>
        ${p.waiting_for ? `<div class="event-meta">waiting for: ${escapeHtml(p.waiting_for)}</div>` : ""}
      </div>
    `).join("");
  }

  if (ex.approvals?.length) {
    out += `<div class="section-title">Approval tasks</div>`;
    out += ex.approvals.map((a) => `
      <div class="detail-section" style="padding:8px 10px;margin-bottom:4px">
        <div class="kv-row">
          <span class="kv-key">${escapeHtml(String(a.task_id || "").slice(0, 8))}</span>
          <span class="kv-val">${escapeHtml((a.assignees || []).join(", ") || "unassigned")}</span>
        </div>
        ${a.due_at ? `<div class="event-meta">due: ${escapeHtml(a.due_at)}</div>` : ""}
      </div>
    `).join("");
  }

  out += `<div style="padding:12px 0 4px">
    <button class="copy-btn" id="explain-copy-btn">Copy explanation JSON</button>
  </div>`;
  out += `</details>`;
  return out;
}
