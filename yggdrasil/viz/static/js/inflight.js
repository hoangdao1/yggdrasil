// In-flight span tracking: renders a "now running" strip and drives node pulses.

import { state, markDirty } from "./state.js";
import { escapeHtml, fmtElapsed, tsOf } from "./format.js";

let inFlightTimer = null;

export function updateInFlightForEvent(event) {
  const t = event.event_type;
  if (t === "tool_call") {
    state.inFlight.set(event.event_id, { event, startedAt: tsOf(event), kind: "tool" });
  } else if (t === "agent_start") {
    state.inFlight.set(event.event_id, { event, startedAt: tsOf(event), kind: "agent" });
  } else if ((t === "tool_result" || t === "agent_end") && event.parent_event_id) {
    state.inFlight.delete(event.parent_event_id);
  } else if (t === "error") {
    for (const [id, span] of state.inFlight) {
      if (span.event.node_id === event.node_id) state.inFlight.delete(id);
    }
  }
}

export function recomputeInFlight() {
  state.inFlight.clear();
  for (const event of state.events) updateInFlightForEvent(event);
}

export function clearInFlight() {
  state.inFlight.clear();
  stopInFlightTicker();
  renderInFlightStrip();
}

export function ensureInFlightTicker() {
  if (inFlightTimer != null) return;
  if (state.inFlight.size === 0) return;
  inFlightTimer = setInterval(tickInFlight, 500);
}

export function stopInFlightTicker() {
  if (inFlightTimer != null) {
    clearInterval(inFlightTimer);
    inFlightTimer = null;
  }
}

function tickInFlight() {
  if (state.inFlight.size === 0) stopInFlightTicker();
  renderInFlightStrip();
  updateInFlightStatusBar();
  // Graph badges and timeline re-read on their own ticks; just mark dirty.
  markDirty("graph", "timeline");
  // Fire a custom event so main.js can run non-data-changing visual updates.
  window.dispatchEvent(new CustomEvent("viz:inflight-tick"));
}

function inFlightOldestMs() {
  let oldest = null;
  for (const span of state.inFlight.values()) {
    if (oldest == null || span.startedAt < oldest) oldest = span.startedAt;
  }
  return oldest == null ? 0 : Date.now() - oldest;
}

export function updateInFlightStatusBar() {
  const count = state.inFlight.size;
  const stat = document.getElementById("stat-inflight");
  const oldestEl = document.getElementById("stat-oldest");
  if (!stat || !oldestEl) return;
  if (count === 0) {
    stat.style.display = "none";
    oldestEl.textContent = "";
    return;
  }
  stat.style.display = "";
  stat.textContent = `${count} in flight`;
  oldestEl.textContent = `oldest ${fmtElapsed(inFlightOldestMs())}`;
}

function inFlightLabel(span) {
  const e = span.event;
  const nodeName = e.node_name || e.node_id || "";
  if (span.kind === "tool") {
    const toolName = e.payload?.tool_name || e.payload?.callable_ref || "tool";
    return `${nodeName} › ${toolName}`;
  }
  return `${nodeName} (agent)`;
}

export function renderInFlightStrip() {
  const strip = document.getElementById("inflight-strip");
  if (!strip) return;
  const spans = [...state.inFlight.values()].sort((a, b) => a.startedAt - b.startedAt);
  if (spans.length === 0) {
    strip.style.display = "none";
    strip.innerHTML = "";
    updateInFlightStatusBar();
    return;
  }
  strip.style.display = "";
  const now = Date.now();
  strip.innerHTML = spans.map((span) => {
    const eid = escapeHtml(span.event.event_id);
    const label = escapeHtml(inFlightLabel(span));
    const elapsed = fmtElapsed(now - span.startedAt);
    const kindClass = span.kind === "tool" ? "inflight-tool" : "inflight-agent";
    return `<div class="inflight-row ${kindClass}" data-event-id="${eid}">`
      + `<span class="inflight-spinner">⟳</span>`
      + `<span class="inflight-label">${label}</span>`
      + `<span class="inflight-timer">${elapsed}</span>`
      + `</div>`;
  }).join("");
  strip.querySelectorAll(".inflight-row[data-event-id]").forEach((el) => {
    el.addEventListener("click", () => {
      const ev = state.eventIndex.get(el.dataset.eventId);
      if (ev) {
        window.dispatchEvent(new CustomEvent("viz:select-event", { detail: { eventId: ev.event_id } }));
      }
    });
  });
  updateInFlightStatusBar();
}

export function getInFlightByNodeId() {
  const runningNodeIds = new Set();
  const oldestByNode = new Map();
  for (const span of state.inFlight.values()) {
    const nid = span.event.node_id;
    if (!nid) continue;
    runningNodeIds.add(nid);
    const prev = oldestByNode.get(nid);
    if (prev == null || span.startedAt < prev) oldestByNode.set(nid, span.startedAt);
  }
  return { runningNodeIds, oldestByNode };
}
