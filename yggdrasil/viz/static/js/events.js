// Events tab: unified list with inline detail drawer, view-mode presets.

import { state, selectFilteredEvents, writeHashState, markDirty } from "./state.js";
import {
  escapeHtml,
  eventTypeClass,
  eventLabel,
  isErrorEvent,
  isRuntimeEvent,
  EVENT_FILTER_ORDER,
} from "./format.js";
import { eventSummary } from "./event-summary.js";
import { renderDetailHtml, bindDetailHandlers } from "./detail.js";

export function renderEventsTab() {
  const container = document.getElementById("tab-events");
  const events = selectFilteredEvents(state.filters);

  if (!events.length) {
    container.innerHTML = "<div class='empty-panel'>No events match the current filters.</div>";
    return;
  }

  let html;
  if (state.filters.viewMode === "tree") {
    html = renderTreeView(events);
  } else if (state.filters.sortMode === "hop") {
    html = groupEventsByHop(events).map((group) =>
      `<div class="event-group"><div class="event-group-title">${escapeHtml(group.title)}</div>${group.events.map((e) => renderEventItem(e)).join("")}</div>`
    ).join("");
  } else {
    html = events.map((e) => renderEventItem(e)).join("");
  }

  container.innerHTML = html;

  // Click handlers for event items → toggle inline drawer
  container.querySelectorAll(".event-item").forEach((element) => {
    element.addEventListener("click", (e) => {
      e.stopPropagation();
      const eventId = element.dataset.eventId;
      const event = state.eventIndex.get(eventId);
      if (event) selectEventInline(event);
    });
  });

  container.querySelectorAll(".log-line[data-event-id]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const ev = state.eventIndex.get(el.dataset.eventId);
      if (ev) selectEventInline(ev);
    });
  });

  container.querySelectorAll(".log-error-ref[data-event-id]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const ev = state.eventIndex.get(el.dataset.eventId);
      if (ev) selectEventInline(ev);
    });
  });

  // Bind any drawer handlers that are already rendered (detail buttons).
  container.querySelectorAll(".event-detail-drawer").forEach((drawer) => {
    bindDetailHandlers(drawer);
  });

  if (!state.finalized) container.scrollTop = container.scrollHeight;
}

function renderEventItem(event) {
  const selected = state.selectedEvent && state.selectedEvent.event_id === event.event_id;
  const error = isErrorEvent(event) ? " error" : "";
  const runtime = isRuntimeEvent(event) ? " runtime" : "";
  const timeStr = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : "";
  const durStr = event.duration_ms != null ? `${event.duration_ms}ms` : "";
  const timeParts = [timeStr, durStr].filter(Boolean).join(" · ");
  const drawer = selected
    ? `<div class="event-detail-drawer">${renderDetailHtml(event)}</div>`
    : "";
  return `
    <div class="event-item${selected ? " selected" : ""}${error}${runtime}" data-event-id="${event.event_id}">
      <div class="event-item-header">
        <div class="event-type ${eventTypeClass(event.event_type)}">${eventLabel(event.event_type)}</div>
        ${timeParts ? `<div class="event-time">${timeParts}</div>` : ""}
      </div>
      <div class="event-node">${escapeHtml(event.node_name || event.node_id)}</div>
      <div class="event-meta">${escapeHtml(eventSummary(event))}</div>
      ${drawer}
    </div>
  `;
}

function groupEventsByHop(events) {
  const groups = [];
  let current = { title: "Before hops", events: [] };
  for (const event of events) {
    if (event.event_type === "hop") {
      if (current.events.length) groups.push(current);
      current = {
        title: `Hop ${event.payload?.hop != null ? event.payload.hop : "?"} · ${event.node_name}`,
        events: [event],
      };
    } else {
      current.events.push(event);
    }
  }
  if (current.events.length) groups.push(current);
  return groups;
}

// ── Tree (log) view ───────────────────────────────────────────────

function renderTreeView(events) {
  const allEvents = state.events;
  const childMap = new Map();
  allEvents.forEach((e) => {
    const pid = e.parent_event_id || null;
    if (!childMap.has(pid)) childMap.set(pid, []);
    childMap.get(pid).push(e);
  });

  const visibleIds = new Set(events.map((e) => e.event_id));
  const lines = [];
  function walk(event, depth) {
    lines.push({ event, depth });
    (childMap.get(event.event_id) || []).forEach((child) => walk(child, depth + 1));
  }
  (childMap.get(null) || []).forEach((root) => walk(root, 0));

  const totalHops = allEvents.filter((e) => e.event_type === "hop").length;
  const totalAgentEnds = allEvents.filter((e) => e.event_type === "agent_end").length;
  const totalMs = allEvents.reduce((acc, e) => acc + (e.duration_ms || 0), 0);
  const errorEvents = allEvents.filter(isErrorEvent);

  let html = '<div class="log-tree">';
  for (const { event, depth } of lines) {
    if (!visibleIds.has(event.event_id) && state.filters.viewMode === "tree" &&
        (state.filters.errorsOnly || state.filters.runtimeOnly || state.filters.eventTypes.size || state.filters.search)) {
      continue;
    }
    const isHop = event.event_type === "hop";
    const isErr = isErrorEvent(event);
    const isSelected = state.selectedEvent?.event_id === event.event_id;
    html += `<div class="log-line${isHop ? " log-line-hop" : ""}${isErr ? " log-line-error" : ""}${isSelected ? " log-line-selected" : ""}" data-event-id="${event.event_id}" style="padding-left:calc(${depth} * 14px + 8px)">${lineContent(event)}</div>`;
    if (isSelected) {
      html += `<div class="event-detail-drawer inline-tree-detail">${renderDetailHtml(event)}</div>`;
    }
  }
  if (errorEvents.length) {
    html += `<div class="log-error-summary"><span class="log-err">✕ ${errorEvents.length} error${errorEvents.length !== 1 ? "s" : ""}</span>`;
    html += errorEvents.map((e) =>
      `<span class="log-error-ref" data-event-id="${e.event_id}"><span class="${eventTypeClass(e.event_type)}">${eventLabel(e.event_type)}</span> ${escapeHtml(e.node_name)}: ${escapeHtml(eventSummary(e).slice(0, 60))}</span>`
    ).join("");
    html += "</div>";
  }
  html += `<div class="log-footer">Total: ${totalHops} hops · ${totalAgentEnds} agent invocations${totalMs > 0 ? ` · ${totalMs}ms` : ""}</div>`;
  html += "</div>";
  return html;
}

function fmtMs(ms) {
  return ms != null ? `<span class="log-ms">[${ms}ms]</span>` : "";
}

function lineContent(event) {
  const t = event.event_type;
  const p = event.payload || {};
  switch (t) {
    case "hop": {
      const nt = String(p.node_type || "").split(".").pop().toUpperCase();
      const hn = p.hop != null ? `hop ${p.hop}` : "hop ?";
      return `<span class="log-hop-num">${escapeHtml(hn)}</span><span class="log-hop-sep">  </span><span class="log-hop-type">${nt}</span><span class="log-hop-sep">  </span><span class="log-hop-name">${escapeHtml(event.node_name)}</span>`;
    }
    case "agent_start": {
      const tools = (p.tools || []).join(", ") || "none";
      const ctx = (p.context || []).join(", ");
      return `<span class="log-kw">tools:</span> <span class="log-tools">${escapeHtml(tools)}</span>${ctx ? `  <span class="log-kw">context:</span> <span class="log-ctx">${escapeHtml(ctx)}</span>` : ""}`;
    }
    case "tool_call": {
      const inp = JSON.stringify(p.input || {});
      const prev = inp.length > 60 ? `${inp.slice(0, 59)}…` : inp;
      return `<span class="log-kw">tool_call</span>  <span class="log-tool-name">${escapeHtml(p.callable_ref || event.node_name)}</span>  <span class="log-json-preview">${escapeHtml(prev)}</span>`;
    }
    case "tool_result": {
      const ok = p.success !== false;
      const sum = (p.output_summary || "").slice(0, 80);
      return `<span class="log-kw">tool_result</span>  <span class="log-tool-name">${escapeHtml(event.node_name)}</span>  <span class="${ok ? "log-ok" : "log-err"}">${ok ? "ok" : "error"}</span>  <span class="log-summary">"${escapeHtml(sum)}"</span>  ${fmtMs(event.duration_ms)}`;
    }
    case "agent_end": {
      const sum = (p.text_summary || "").slice(0, 100);
      return `<span class="log-kw">agent_end</span>  <span class="log-summary">"${escapeHtml(sum)}"</span>  <span class="log-intent">intent=${escapeHtml(p.intent || "default")}</span>  ${fmtMs(event.duration_ms)}`;
    }
    case "error":
      return `<span class="log-kw log-err">fatal error</span>  <span class="log-err">${escapeHtml(p.error_type || "Error")}</span>  <span class="log-summary">${escapeHtml(p.error || "")}</span>`;
    default:
      return `<span class="log-kw">${escapeHtml(t)}</span>  <span class="log-dim">${escapeHtml(eventSummary(event))}</span>`;
  }
}

// ── Selection helper used by all click sites ────────────────────

export function selectEventInline(event) {
  const wasSelected = state.selectedEvent?.event_id === event.event_id;
  state.selectedEvent = wasSelected ? null : event;
  writeHashState();
  markDirty("events", "graph", "timeline");
  window.dispatchEvent(new CustomEvent("viz:flush-dirty"));
}

// ── Filter chip row ──────────────────────────────────────────────

export function renderFilterChips() {
  const container = document.getElementById("event-filter-row");
  if (!container) return;
  container.innerHTML = EVENT_FILTER_ORDER.map((type) => {
    const active = state.filters.eventTypes.has(type) ? "active" : "";
    const count = state.summary?.counts?.[type] || 0;
    return `<button type="button" class="filter-chip ${active}" data-type="${type}">${eventLabel(type)} · ${count}</button>`;
  }).join("");
  container.querySelectorAll(".filter-chip").forEach((button) => {
    button.addEventListener("click", () => {
      const type = button.dataset.type;
      if (state.filters.eventTypes.has(type)) state.filters.eventTypes.delete(type);
      else state.filters.eventTypes.add(type);
      writeHashState();
      markDirty("filterChips", "events");
      window.dispatchEvent(new CustomEvent("viz:flush-dirty"));
    });
  });
}
