// Central store, hash-state sync, memoized selectors, dirty-flag bookkeeping.

import {
  EVENT_FILTER_ORDER,
  RUNTIME_EVENT_TYPES,
  isErrorEvent,
  isRuntimeEvent,
} from "./format.js";

export const state = {
  events: [],
  eventIndex: new Map(),
  meta: null,
  summary: null,
  finalized: false,
  connectionState: "connecting",
  selectedEvent: null,
  activeTab: "run",
  graphState: null,
  explain: null,
  explainLoading: false,
  filters: {
    search: "",
    errorsOnly: false,
    runtimeOnly: false,
    sortMode: "chronological",
    viewMode: "list", // list | tree
    eventTypes: new Set(),
  },
  traceLens: "flow",
  traceNodes: new Map(),
  traceEdges: {
    flow: new Map(),
    composition: new Map(),
  },
  inFlight: new Map(),
  eventVersion: 0,
  dirty: {
    run: true,
    events: true,
    graph: true,
    timeline: true,
    database: true,
    statusBar: true,
    inflight: true,
    filterChips: true,
  },
};

export function markDirty(...keys) {
  for (const k of keys) state.dirty[k] = true;
}

export function markAllDirty() {
  for (const k of Object.keys(state.dirty)) state.dirty[k] = true;
}

export function bumpEventVersion() {
  state.eventVersion += 1;
}

// ── Hash state ───────────────────────────────────────────────────

const VALID_TABS = new Set(["run", "events", "database"]);

export function readHashState() {
  const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  const eventTypes = params.get("types");
  return {
    tab: params.get("tab") || "run",
    eventId: params.get("event") || null,
    search: params.get("search") || "",
    errorsOnly: params.get("errors") === "1",
    runtimeOnly: params.get("runtime") === "1",
    sortMode: params.get("sort") || "chronological",
    viewMode: params.get("view") === "tree" ? "tree" : "list",
    lens: params.get("lens") || "flow",
    eventTypes: eventTypes ? eventTypes.split(",").filter(Boolean) : [],
  };
}

export function writeHashState() {
  const params = new URLSearchParams();
  params.set("tab", state.activeTab);
  if (state.selectedEvent) params.set("event", state.selectedEvent.event_id);
  if (state.filters.search) params.set("search", state.filters.search);
  if (state.filters.errorsOnly) params.set("errors", "1");
  if (state.filters.runtimeOnly) params.set("runtime", "1");
  if (state.filters.sortMode !== "chronological") params.set("sort", state.filters.sortMode);
  if (state.filters.viewMode === "tree") params.set("view", "tree");
  if (state.traceLens !== "flow") params.set("lens", state.traceLens);
  if (state.filters.eventTypes.size) params.set("types", [...state.filters.eventTypes].join(","));
  const hash = params.toString();
  history.replaceState(null, "", `${location.pathname}${location.search}${hash ? `#${hash}` : ""}`);
}

export function applyHashState() {
  const h = readHashState();
  state.activeTab = VALID_TABS.has(h.tab) ? h.tab : "run";
  state.filters.search = h.search;
  state.filters.errorsOnly = h.errorsOnly;
  state.filters.runtimeOnly = h.runtimeOnly;
  state.filters.sortMode = h.sortMode;
  state.filters.viewMode = h.viewMode;
  state.traceLens = h.lens === "composition" ? "composition" : "flow";
  state.filters.eventTypes = new Set(h.eventTypes);
}

export function restoreHashEventSelection() {
  const { eventId } = readHashState();
  if (eventId && state.eventIndex.has(eventId)) {
    state.selectedEvent = state.eventIndex.get(eventId);
  }
}

// ── Memoized selectors ───────────────────────────────────────────

const memoCache = new Map();

function memo(key, fn) {
  const entry = memoCache.get(key);
  if (entry && entry.v === state.eventVersion) return entry.value;
  const value = fn();
  memoCache.set(key, { v: state.eventVersion, value });
  return value;
}

export function selectCounts() {
  return memo("counts", () => {
    const counts = {};
    for (const e of state.events) counts[e.event_type] = (counts[e.event_type] || 0) + 1;
    return counts;
  });
}

export function selectAgentNames() {
  return memo("agentNames", () => {
    const seen = new Set();
    for (const e of state.events) if (e.event_type === "agent_start") seen.add(e.node_name);
    return [...seen];
  });
}

export function selectToolNames() {
  return memo("toolNames", () => {
    const seen = new Set();
    for (const e of state.events) if (e.event_type === "tool_call") seen.add(e.node_name);
    return [...seen];
  });
}

export function selectErrorEvents() {
  return memo("errors", () => state.events.filter(isErrorEvent));
}

// Per-node stats for graph badges.
// Returns Map<nodeId, { toolCalls, errors, totalMs }>
export function selectNodeStats() {
  return memo("nodeStats", () => {
    const stats = new Map();
    const get = (id) => {
      let s = stats.get(id);
      if (!s) {
        s = { toolCalls: 0, errors: 0, totalMs: 0, hops: 0 };
        stats.set(id, s);
      }
      return s;
    };
    for (const e of state.events) {
      if (!e.node_id) continue;
      const s = get(e.node_id);
      if (e.event_type === "tool_call") s.toolCalls += 1;
      if (e.event_type === "hop") s.hops += 1;
      if (isErrorEvent(e)) s.errors += 1;
      if (e.duration_ms != null) s.totalMs += e.duration_ms;
    }
    return stats;
  });
}

// Timeline ticks: hop boundaries, errors, pauses.
export function selectTimelineTicks() {
  return memo("timelineTicks", () => {
    const ticks = [];
    for (const e of state.events) {
      const ts = e.timestamp ? new Date(e.timestamp).getTime() : null;
      if (!ts) continue;
      if (e.event_type === "hop") ticks.push({ kind: "hop", ts, event: e });
      else if (e.event_type === "pause") ticks.push({ kind: "pause", ts, event: e });
      else if (isErrorEvent(e)) ticks.push({ kind: "error", ts, event: e });
    }
    return ticks;
  });
}

export function selectTimeRange() {
  return memo("timeRange", () => {
    let lo = null;
    let hi = null;
    for (const e of state.events) {
      if (!e.timestamp) continue;
      const t = new Date(e.timestamp).getTime();
      if (Number.isNaN(t)) continue;
      if (lo == null || t < lo) lo = t;
      if (hi == null || t > hi) hi = t;
    }
    return { lo, hi };
  });
}

// Filtered events used by the Events list.
export function selectFilteredEvents(filters) {
  const search = filters.search.trim().toLowerCase();
  return state.events.filter((event) => {
    if (filters.errorsOnly && !isErrorEvent(event)) return false;
    if (filters.runtimeOnly && !isRuntimeEvent(event)) return false;
    if (filters.eventTypes.size && !filters.eventTypes.has(event.event_type)) return false;
    if (!search) return true;
    const payload = JSON.stringify(event.payload || {}).toLowerCase();
    const haystack = [
      event.event_type,
      event.node_name,
      event.node_id,
      payload,
    ].join(" ");
    return haystack.includes(search);
  });
}

export function nodeNameForId(id) {
  if (!id) return "end";
  const node = state.traceNodes.get(id);
  return node ? node.name : String(id).slice(0, 8);
}

export { EVENT_FILTER_ORDER, RUNTIME_EVENT_TYPES };
