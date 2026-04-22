// WebSocket transport + event dispatch. All events route through handleX which
// mutates state and sets dirty flags; main.js listens for `viz:flush-dirty` to
// actually render.

import { state, bumpEventVersion, markDirty, markAllDirty, restoreHashEventSelection } from "./state.js";
import { ingestEvent } from "./ingest.js";
import {
  updateInFlightForEvent,
  recomputeInFlight,
  ensureInFlightTicker,
  stopInFlightTicker,
} from "./inflight.js";
import { markDbNeedsRebuild } from "./database.js";
import { fetchExplain } from "./run.js";

export function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  state.connectionState = "connecting";
  fire();

  ws.onopen = () => {
    state.connectionState = "live";
    fire();
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 15000);
  };

  ws.onclose = () => {
    state.connectionState = state.finalized ? "done" : "reconnecting";
    fire();
    if (!state.finalized) setTimeout(connect, 2000);
  };

  ws.onerror = () => {
    state.connectionState = "error";
    fire();
  };

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "meta") handleMeta(message.data);
    else if (message.type === "event") handleEvent(message.data);
    else if (message.type === "graph_state") handleGraphState(message.data);
    else if (message.type === "summary") handleSummary(message.data);
    else if (message.type === "finalize") handleFinalize(message.data);
  };
}

function fire() {
  window.dispatchEvent(new CustomEvent("viz:flush-dirty"));
}

function handleMeta(data) {
  state.meta = data;
  const queryEl = document.getElementById("query-text");
  if (queryEl) {
    queryEl.textContent = data.query || "";
    queryEl.title = data.query || "";
  }
  const sessEl = document.getElementById("session-id-text");
  if (sessEl) sessEl.textContent = (data.session_id || "").slice(0, 8);
  markDirty("run");
  fire();
}

function handleSummary(data) {
  state.summary = data;
  recomputeInFlight();
  markDirty("run", "filterChips", "statusBar", "inflight");
  ensureInFlightTicker();
  fire();
}

function handleEvent(event) {
  state.events.push(event);
  state.eventIndex.set(event.event_id, event);
  bumpEventVersion();
  ingestEvent(event);
  updateInFlightForEvent(event);
  if (!state.selectedEvent) state.selectedEvent = event;
  markDirty("run", "events", "graph", "timeline", "statusBar", "inflight", "database");
  ensureInFlightTicker();
  restoreHashEventSelection();
  fire();
}

function handleGraphState(data) {
  state.graphState = data;
  markDbNeedsRebuild();
  markDirty("run", "database");
  fire();
}

function handleFinalize(data) {
  state.finalized = true;
  state.connectionState = "done";
  state.meta = { session_id: data.session_id, query: data.query };
  state.summary = data.summary || state.summary;
  state.graphState = data.graph_state || state.graphState;
  markDbNeedsRebuild();

  const queryEl = document.getElementById("query-text");
  if (queryEl) {
    queryEl.textContent = data.query || "";
    queryEl.title = data.query || "";
  }
  const sessEl = document.getElementById("session-id-text");
  if (sessEl) sessEl.textContent = (data.session_id || "").slice(0, 8);

  if (Array.isArray(data.events) && data.events.length > 0) {
    state.events = data.events;
    state.eventIndex = new Map();
    state.traceNodes.clear();
    state.traceEdges.flow.clear();
    state.traceEdges.composition.clear();
    data.events.forEach((event) => {
      state.eventIndex.set(event.event_id, event);
      ingestEvent(event);
    });
    bumpEventVersion();
    restoreHashEventSelection();
  }

  state.inFlight.clear();
  stopInFlightTicker();

  markAllDirty();
  fire();
  fetchExplain();
}
