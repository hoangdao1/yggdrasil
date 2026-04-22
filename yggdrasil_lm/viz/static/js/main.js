// Entry point: controls, tab switching, dirty-flag render loop.

import { state, applyHashState, writeHashState, markDirty, markAllDirty } from "./state.js";
import { connect } from "./ws.js";
import { updateConnectionBadge, updateStatusBar, updateGraphEmptyState } from "./status.js";
import { renderRunTab } from "./run.js";
import { renderEventsTab, renderFilterChips, selectEventInline } from "./events.js";
import { renderGraph, fitTraceGraph, resetTraceGraph, centerSelectedTraceNode, updateInFlightGraphBadges, renderTimelineStrip } from "./graph.js";
import { renderDatabase, renderDatabaseCanvas } from "./database.js";
import { renderInFlightStrip, ensureInFlightTicker } from "./inflight.js";

const VALID_TABS = ["run", "events", "database"];

function flushDirty() {
  if (state.dirty.statusBar) {
    updateConnectionBadge();
    updateStatusBar();
    updateGraphEmptyState();
    state.dirty.statusBar = false;
  }
  if (state.dirty.inflight) {
    renderInFlightStrip();
    state.dirty.inflight = false;
  }
  if (state.dirty.filterChips) {
    renderFilterChips();
    state.dirty.filterChips = false;
  }

  // Active sidebar tab is always rendered if dirty.
  const tab = state.activeTab;
  if (tab === "run" && state.dirty.run) {
    renderRunTab();
    state.dirty.run = false;
  } else if (tab === "events" && state.dirty.events) {
    renderEventsTab();
    state.dirty.events = false;
  } else if (tab === "database" && state.dirty.database) {
    renderDatabase();
    state.dirty.database = false;
  }

  // Graph is visible whenever the active tab is not `database`.
  if (tab !== "database") {
    if (state.dirty.graph) {
      renderGraph();
      state.dirty.graph = false;
      state.dirty.timeline = false; // graph renders timeline too
    } else if (state.dirty.timeline) {
      renderTimelineStrip();
      state.dirty.timeline = false;
    }
  }
}

function bindControls() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => setTab(tab.dataset.tab));
    tab.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        setTab(tab.dataset.tab);
      }
    });
  });

  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.value = state.filters.search;
    searchInput.addEventListener("input", (event) => {
      state.filters.search = event.target.value;
      writeHashState();
      markDirty("events");
      flushDirty();
    });
  }

  const sortSelect = document.getElementById("sort-mode");
  if (sortSelect) {
    sortSelect.value = state.filters.sortMode;
    sortSelect.addEventListener("change", (event) => {
      state.filters.sortMode = event.target.value;
      writeHashState();
      markDirty("events");
      flushDirty();
    });
  }

  const viewSelect = document.getElementById("view-mode");
  if (viewSelect) {
    viewSelect.value = state.filters.viewMode;
    viewSelect.addEventListener("change", (event) => {
      state.filters.viewMode = event.target.value;
      writeHashState();
      markDirty("events");
      flushDirty();
    });
  }

  bindToggle("errors-only-btn", () => {
    state.filters.errorsOnly = !state.filters.errorsOnly;
    document.getElementById("errors-only-btn").classList.toggle("active", state.filters.errorsOnly);
    markDirty("events");
  });

  bindToggle("runtime-only-btn", () => {
    state.filters.runtimeOnly = !state.filters.runtimeOnly;
    document.getElementById("runtime-only-btn").classList.toggle("active", state.filters.runtimeOnly);
    markDirty("events");
  });

  document.getElementById("trace-lens-flow")?.addEventListener("click", () => setTraceLens("flow"));
  document.getElementById("trace-lens-composition")?.addEventListener("click", () => setTraceLens("composition"));
  document.getElementById("trace-fit-btn")?.addEventListener("click", fitTraceGraph);
  document.getElementById("trace-reset-btn")?.addEventListener("click", resetTraceGraph);
  document.getElementById("trace-center-btn")?.addEventListener("click", centerSelectedTraceNode);
}

function bindToggle(id, handler) {
  const btn = document.getElementById(id);
  if (!btn) return;
  btn.addEventListener("click", () => {
    handler();
    writeHashState();
    flushDirty();
  });
}

function setTab(name) {
  if (!VALID_TABS.includes(name)) return;
  state.activeTab = name;
  document.querySelectorAll(".tab").forEach((tab) => {
    const active = tab.dataset.tab === name;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", active ? "true" : "false");
  });
  for (const tabName of VALID_TABS) {
    const el = document.getElementById(`tab-${tabName}`);
    if (el) el.style.display = tabName === name ? "" : "none";
  }

  const showDatabase = name === "database";
  document.getElementById("graph-svg").style.display = showDatabase ? "none" : "block";
  document.getElementById("trace-toolbar").style.display = showDatabase ? "none" : "flex";
  document.getElementById("timeline-strip").style.display = showDatabase ? "none" : "";
  document.getElementById("graph-empty").style.display =
    showDatabase ? "none" : (state.traceNodes.size ? "none" : "flex");
  document.getElementById("db-svg").style.display = showDatabase ? "block" : "none";
  document.getElementById("db-toolbar").style.display = showDatabase ? "flex" : "none";
  document.getElementById("db-empty").style.display = showDatabase && !state.graphState ? "flex" : "none";
  document.getElementById("triage-bar").style.display = name === "events" ? "flex" : "none";

  if (showDatabase) renderDatabaseCanvas();
  writeHashState();
  // Ensure the now-active tab is re-rendered.
  markDirty(name);
  flushDirty();
}

function setTraceLens(lens) {
  state.traceLens = lens;
  document.getElementById("trace-lens-flow").classList.toggle("active", lens === "flow");
  document.getElementById("trace-lens-composition").classList.toggle("active", lens === "composition");
  writeHashState();
  markDirty("graph");
  flushDirty();
}

// ── Wire cross-module events ────────────────────────────────────

window.addEventListener("viz:flush-dirty", () => flushDirty());
window.addEventListener("viz:inflight-tick", () => {
  updateInFlightGraphBadges();
});
window.addEventListener("viz:select-event", (e) => {
  const eid = e.detail?.eventId;
  if (!eid) return;
  const ev = state.eventIndex.get(eid);
  if (!ev) return;
  state.selectedEvent = ev;
  writeHashState();
  markDirty("events", "graph", "timeline");
  // Jump to Events tab if coming from graph/timeline/inflight strip, so the
  // detail drawer is visible.
  if (state.activeTab !== "events" && state.activeTab !== "database") {
    setTab("events");
  } else {
    flushDirty();
  }
});

// ── Boot ────────────────────────────────────────────────────────

applyHashState();

// Apply filter-button active states from hash.
const errBtn = document.getElementById("errors-only-btn");
if (errBtn) errBtn.classList.toggle("active", state.filters.errorsOnly);
const runtBtn = document.getElementById("runtime-only-btn");
if (runtBtn) runtBtn.classList.toggle("active", state.filters.runtimeOnly);

bindControls();
markAllDirty();
document.getElementById("trace-lens-flow")?.classList.toggle("active", state.traceLens === "flow");
document.getElementById("trace-lens-composition")?.classList.toggle("active", state.traceLens === "composition");
setTab(state.activeTab);
connect();
