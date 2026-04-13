// Trace graph (flow + composition lenses), timeline strip, per-node badges.

import { state } from "./state.js";
import {
  nodeColor,
  nodeStroke,
  fmtElapsed,
  fmtDurationMs,
  escapeHtml,
  eventLabel,
} from "./format.js";
import {
  selectNodeStats,
  selectTimelineTicks,
  selectTimeRange,
} from "./state.js";
import { getInFlightByNodeId } from "./inflight.js";

let graphZoom = null;
let graphRoot = null;
let graphSimulation = null;
let graphNodeSelection = null;
let graphLinkSelection = null;
let graphCurrentNodes = [];
let graphCurrentLinks = [];

export function renderGraph() {
  const svg = d3.select("#graph-svg");
  const empty = document.getElementById("graph-empty");
  const pane = document.getElementById("graph-pane");

  if (!state.traceNodes.size) {
    empty.style.display = "flex";
    return;
  }
  empty.style.display = "none";

  const width = svg.node().clientWidth || pane.clientWidth || 600;
  const height = svg.node().clientHeight || pane.clientHeight || 400;
  const nodes = [...state.traceNodes.values()].filter((node) => {
    if (state.traceLens === "flow") return node.category === "graph";
    return true;
  }).map((node) => ({ ...node }));
  const nodeIds = new Set(nodes.map((node) => node.id));
  const links = [...state.traceEdges[state.traceLens].values()]
    .filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
    .map((edge) => ({ ...edge }));

  graphCurrentNodes = nodes;
  graphCurrentLinks = links;

  svg.selectAll("*").remove();
  const defs = svg.append("defs");
  defs.append("marker").attr("id", "arrow").attr("markerWidth", 8).attr("markerHeight", 6)
    .attr("refX", 22).attr("refY", 3).attr("orient", "auto")
    .append("path").attr("d", "M0,0 L8,3 L0,6 Z").attr("fill", "#30363d");

  graphRoot = svg.append("g");
  graphZoom = d3.zoom().scaleExtent([0.2, 4]).on("zoom", (e) => graphRoot.attr("transform", e.transform));
  svg.call(graphZoom);

  const relatedNodeIds = selectedNodeNeighborhood();
  const relatedLinkKeys = selectedLinkNeighborhood();

  graphLinkSelection = graphRoot.append("g").selectAll("line")
    .data(links)
    .join("line")
    .attr("class", (d) => {
      const key = `${d.source}->${d.target}`;
      const hasSelection = relatedNodeIds.size > 0;
      return `link active${relatedLinkKeys.has(key) ? " related" : ""}${hasSelection && !relatedLinkKeys.has(key) ? " dimmed" : ""}`;
    });

  graphNodeSelection = graphRoot.append("g").selectAll("g")
    .data(nodes)
    .join("g")
    .attr("class", (d) => {
      const selected = isNodeSelected(d.id) ? " selected" : "";
      const related = relatedNodeIds.has(d.id) ? " related" : "";
      const dimmed = relatedNodeIds.size > 0 && !relatedNodeIds.has(d.id) ? " dimmed" : "";
      return `node${selected}${related}${dimmed}`;
    })
    .call(d3.drag()
      .on("start", (e, d) => {
        if (!e.active) graphSimulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on("drag", (e, d) => {
        d.fx = e.x;
        d.fy = e.y;
      })
      .on("end", (e, d) => {
        if (!e.active) graphSimulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }))
    .on("click", (_, d) => {
      const event = [...state.events].reverse().find(
        (candidate) => candidate.node_id === d.refNodeId || candidate.node_name === d.name,
      );
      if (event) {
        window.dispatchEvent(new CustomEvent("viz:select-event", { detail: { eventId: event.event_id } }));
      }
    });

  graphNodeSelection.append("circle")
    .attr("r", 22)
    .attr("fill", (d) => nodeColor(d.type))
    .attr("stroke", (d) => nodeStroke(d.type));

  graphNodeSelection.append("text")
    .attr("class", "node-label")
    .attr("dy", "0.35em")
    .text((d) => d.name.length > 16 ? `${d.name.slice(0, 15)}…` : d.name);

  graphNodeSelection.filter((d) => d.hopOrder !== undefined)
    .append("text")
    .attr("class", "node-hop")
    .attr("x", 16)
    .attr("y", -16)
    .text((d) => d.hopOrder);

  graphSimulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d) => d.id).distance(state.traceLens === "flow" ? 130 : 100))
    .force("charge", d3.forceManyBody().strength(-320))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(46))
    .on("tick", () => {
      graphLinkSelection
        .attr("x1", (d) => d.source.x || 0)
        .attr("y1", (d) => d.source.y || 0)
        .attr("x2", (d) => d.target.x || 0)
        .attr("y2", (d) => d.target.y || 0);
      graphNodeSelection.attr("transform", (d) => `translate(${d.x || 0},${d.y || 0})`);
    });

  fitTraceGraph();
  updateNodeBadges();
  updateInFlightGraphBadges();
  renderTimelineStrip();
}

function isNodeSelected(nodeId) {
  if (!state.selectedEvent) return false;
  const selectedNode = state.traceNodes.get(state.selectedEvent.node_id);
  return selectedNode?.id === nodeId || state.selectedEvent.node_id === nodeId;
}

function selectedNodeNeighborhood() {
  if (!state.selectedEvent) return new Set();
  const selectedId = state.selectedEvent.node_id;
  const related = new Set([selectedId]);
  graphCurrentLinks.forEach((link) => {
    if (link.source === selectedId || link.target === selectedId) {
      related.add(link.source);
      related.add(link.target);
    }
  });
  return related;
}

function selectedLinkNeighborhood() {
  const keys = new Set();
  if (!state.selectedEvent) return keys;
  const selectedId = state.selectedEvent.node_id;
  graphCurrentLinks.forEach((link) => {
    if (link.source === selectedId || link.target === selectedId) {
      keys.add(`${link.source}->${link.target}`);
    }
  });
  return keys;
}

export function fitTraceGraph() {
  const svg = d3.select("#graph-svg");
  if (!graphRoot || !graphCurrentNodes.length) return;
  const bounds = graphRoot.node().getBBox();
  const fullWidth = svg.node().clientWidth || 800;
  const fullHeight = svg.node().clientHeight || 600;
  if (!bounds.width || !bounds.height) return;
  const scale = Math.min(2.5, 0.85 / Math.max(bounds.width / fullWidth, bounds.height / fullHeight));
  const translateX = fullWidth / 2 - scale * (bounds.x + bounds.width / 2);
  const translateY = fullHeight / 2 - scale * (bounds.y + bounds.height / 2);
  svg.transition().duration(250).call(graphZoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
}

export function resetTraceGraph() {
  const svg = d3.select("#graph-svg");
  if (!graphZoom) return;
  svg.transition().duration(200).call(graphZoom.transform, d3.zoomIdentity);
}

export function centerSelectedTraceNode() {
  if (!state.selectedEvent || !graphZoom || !graphNodeSelection) return;
  const selected = graphCurrentNodes.find((node) => node.id === state.selectedEvent.node_id);
  if (!selected) return;
  const svg = d3.select("#graph-svg");
  const width = svg.node().clientWidth || 800;
  const height = svg.node().clientHeight || 600;
  svg.transition().duration(250).call(
    graphZoom.transform,
    d3.zoomIdentity.translate(width / 2 - (selected.x || 0), height / 2 - (selected.y || 0)).scale(1.2),
  );
}

// ── Per-node badges (heat map overlay) ────────────────────────────

export function updateNodeBadges() {
  if (!graphNodeSelection) return;
  const stats = selectNodeStats();
  graphNodeSelection.each(function (d) {
    const g = d3.select(this);
    const s = stats.get(d.refNodeId);
    let badge = g.select("text.node-badge");
    if (!s || (s.toolCalls === 0 && s.errors === 0 && !s.totalMs)) {
      if (!badge.empty()) badge.remove();
      return;
    }
    if (badge.empty()) {
      badge = g.append("text")
        .attr("class", "node-badge")
        .attr("x", 0)
        .attr("y", 42)
        .attr("text-anchor", "middle");
    }
    const parts = [];
    if (s.toolCalls) parts.push(`${s.toolCalls} calls`);
    if (s.errors) parts.push(`${s.errors} err`);
    if (s.totalMs) parts.push(fmtDurationMs(s.totalMs));
    badge.text(parts.join(" · "));
    badge.classed("has-errors", s.errors > 0);
  });

  // Heat intensity by duration — scale stroke-width modestly.
  let maxMs = 0;
  for (const s of stats.values()) if (s.totalMs > maxMs) maxMs = s.totalMs;
  graphNodeSelection.select("circle").attr("stroke-width", (d) => {
    const s = stats.get(d.refNodeId);
    if (!s || !maxMs) return 2;
    return 2 + Math.round((s.totalMs / maxMs) * 3);
  });
}

export function updateInFlightGraphBadges() {
  if (!graphNodeSelection) return;
  const { runningNodeIds, oldestByNode } = getInFlightByNodeId();
  const now = Date.now();
  graphNodeSelection.classed("node-running", (d) => runningNodeIds.has(d.refNodeId));
  graphNodeSelection.each(function (d) {
    const g = d3.select(this);
    const startedAt = oldestByNode.get(d.refNodeId);
    let timer = g.select("text.node-timer");
    if (startedAt != null) {
      if (timer.empty()) {
        timer = g.append("text")
          .attr("class", "node-timer")
          .attr("x", 0)
          .attr("y", -30)
          .attr("text-anchor", "middle");
      }
      timer.text(fmtElapsed(now - startedAt));
    } else if (!timer.empty()) {
      timer.remove();
    }
  });
}

// ── Timeline strip ────────────────────────────────────────────────

export function renderTimelineStrip() {
  const container = document.getElementById("timeline-strip");
  if (!container) return;
  const ticks = selectTimelineTicks();
  const { lo, hi } = selectTimeRange();
  if (!lo || !hi || hi === lo || !ticks.length) {
    container.style.display = "none";
    container.innerHTML = "";
    return;
  }
  container.style.display = "";
  const span = hi - lo;
  const selectedId = state.selectedEvent?.event_id || null;
  const items = ticks.map((tick) => {
    const pct = ((tick.ts - lo) / span) * 100;
    const cls = `timeline-tick timeline-${tick.kind}${tick.event.event_id === selectedId ? " selected" : ""}`;
    const title = `${eventLabel(tick.event.event_type)} — ${escapeHtml(tick.event.node_name || tick.event.node_id || "")}`;
    return `<div class="${cls}" style="left:${pct}%" data-event-id="${escapeHtml(tick.event.event_id)}" title="${title}"></div>`;
  }).join("");
  const totalMs = span;
  const durLabel = fmtDurationMs(totalMs);
  container.innerHTML = `
    <div class="timeline-track">${items}</div>
    <div class="timeline-labels">
      <span>0</span>
      <span class="timeline-ticks-legend">${ticks.length} ticks · ${durLabel}</span>
      <span>${durLabel}</span>
    </div>
  `;
  container.querySelectorAll(".timeline-tick[data-event-id]").forEach((el) => {
    el.addEventListener("click", () => {
      window.dispatchEvent(new CustomEvent("viz:select-event", { detail: { eventId: el.dataset.eventId } }));
    });
  });
}
