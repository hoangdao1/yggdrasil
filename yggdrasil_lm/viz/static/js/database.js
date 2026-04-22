// Database canvas + sidebar. Lifted verbatim from the old app.js.

import { state } from "./state.js";
import { nodeColor, nodeStroke, escapeHtml, prettyJson } from "./format.js";

const DB_BATCH_SIZE = 100;
let dbZoom = null;
let dbRoot = null;
let dbSim = null;
let dbNodes = [];
let dbLinks = [];
let dbAllNodes = [];
let dbAllLinks = [];
let dbSelectedNode = null;
export let dbNeedsRebuild = false;

export function markDbNeedsRebuild() {
  dbNeedsRebuild = true;
}

function buildDbGraphData() {
  const db = state.graphState;
  if (!db) return;
  dbAllNodes = [];
  dbAllLinks = [];
  const ids = new Set();
  Object.entries(db.nodes_by_type || {}).forEach(([type, nodes]) => {
    nodes.forEach((node) => {
      dbAllNodes.push({
        id: node.node_id,
        name: node.name || node.node_id.slice(0, 8),
        type,
        is_valid: node.is_valid,
        raw: node,
      });
      ids.add(node.node_id);
    });
  });
  Object.entries(db.edges_by_type || {}).forEach(([type, edges]) => {
    edges.forEach((edge) => {
      if (ids.has(edge.src_id) && ids.has(edge.dst_id)) {
        dbAllLinks.push({
          source: edge.src_id,
          target: edge.dst_id,
          type,
          is_valid: edge.is_valid,
          raw: edge,
        });
      }
    });
  });
}

function renderDbSimulation() {
  const svg = d3.select("#db-svg");
  const empty = document.getElementById("db-empty");
  if (!dbNodes.length) {
    empty.style.display = "flex";
    return;
  }
  empty.style.display = "none";

  const pane = document.getElementById("graph-pane");
  const width = pane.clientWidth || 800;
  const height = pane.clientHeight || 600;
  svg.attr("width", width).attr("height", height);

  if (dbSim) dbSim.stop();
  svg.selectAll("*").remove();

  const defs = svg.append("defs");
  defs.append("marker").attr("id", "db-arrow").attr("markerWidth", 8).attr("markerHeight", 6)
    .attr("refX", 22).attr("refY", 3).attr("orient", "auto")
    .append("path").attr("d", "M0,0 L8,3 L0,6 Z").attr("fill", "#30363d");

  dbRoot = svg.append("g");
  dbZoom = d3.zoom().scaleExtent([0.05, 6]).on("zoom", (e) => dbRoot.attr("transform", e.transform));
  svg.call(dbZoom);

  const linkSelection = dbRoot.append("g").selectAll("line")
    .data(dbLinks)
    .join("line")
    .attr("class", "link")
    .attr("stroke-opacity", (d) => d.is_valid ? 1 : 0.3)
    .attr("marker-end", "url(#db-arrow)");

  const nodeSelection = dbRoot.append("g").selectAll("g")
    .data(dbNodes, (d) => d.id)
    .join("g")
    .attr("class", "node")
    .call(d3.drag()
      .on("start", (e, d) => {
        if (!e.active) dbSim.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on("drag", (e, d) => {
        d.fx = e.x;
        d.fy = e.y;
      })
      .on("end", (e, d) => {
        if (!e.active) dbSim.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }))
    .on("click", (e, d) => {
      dbSelectedNode = d.raw;
      dbRoot.selectAll(".node").classed("db-selected", false);
      d3.select(e.currentTarget).classed("db-selected", true);
      renderDatabaseSidebar();
    });

  nodeSelection.append("circle")
    .attr("r", 20)
    .attr("fill", (d) => nodeColor(d.type))
    .attr("stroke", (d) => nodeStroke(d.type))
    .attr("opacity", (d) => d.is_valid ? 1 : 0.45);

  nodeSelection.append("text")
    .attr("dy", "0.35em")
    .text((d) => d.name.length > 14 ? `${d.name.slice(0, 13)}…` : d.name);

  nodeSelection.filter((d) => !d.is_valid)
    .append("circle")
    .attr("r", 5)
    .attr("cx", 14)
    .attr("cy", -14)
    .attr("fill", "#f85149");

  dbSim = d3.forceSimulation(dbNodes)
    .force("link", d3.forceLink(dbLinks).id((d) => d.id).distance(90))
    .force("charge", d3.forceManyBody().strength(-180))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(32))
    .on("tick", () => {
      linkSelection
        .attr("x1", (d) => d.source.x || 0)
        .attr("y1", (d) => d.source.y || 0)
        .attr("x2", (d) => d.target.x || 0)
        .attr("y2", (d) => d.target.y || 0);
      nodeSelection.attr("transform", (d) => `translate(${d.x || 0},${d.y || 0})`);
    });

  for (let i = 0; i < 100; i += 1) dbSim.tick();
  updateDbToolbar();
  fitDbGraph();
}

export function fitDbGraph() {
  const svg = d3.select("#db-svg");
  if (!dbRoot || !dbNodes.length) return;
  const bounds = dbRoot.node().getBBox();
  const width = svg.node().clientWidth || 800;
  const height = svg.node().clientHeight || 600;
  if (!bounds.width || !bounds.height) return;
  const scale = Math.min(2.2, 0.88 / Math.max(bounds.width / width, bounds.height / height));
  const translateX = width / 2 - scale * (bounds.x + bounds.width / 2);
  const translateY = height / 2 - scale * (bounds.y + bounds.height / 2);
  svg.transition().duration(250).call(dbZoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
}

export function resetDbGraph() {
  const svg = d3.select("#db-svg");
  if (!dbZoom) return;
  svg.transition().duration(200).call(dbZoom.transform, d3.zoomIdentity);
}

function loadMoreDbNodes() {
  const current = dbNodes.length;
  if (current >= dbAllNodes.length) return;
  const nextCount = Math.min(current + DB_BATCH_SIZE, dbAllNodes.length);
  dbNodes.push(...dbAllNodes.slice(current, nextCount).map((n) => ({ ...n })));
  const loadedIds = new Set(dbNodes.map((n) => n.id));
  dbLinks = dbAllLinks.filter((e) => loadedIds.has(e.source) && loadedIds.has(e.target)).map((e) => ({ ...e }));
  renderDbSimulation();
  renderDatabaseSidebar();
}

function updateDbToolbar() {
  const toolbar = document.getElementById("db-toolbar");
  const loaded = dbNodes.length;
  const total = dbAllNodes.length;
  const remaining = total - loaded;
  const legend = [
    ["Agent", "#79c0ff", "#1f4068"],
    ["Tool", "#e3b341", "#4a3000"],
    ["Context", "#58a6ff", "#003b4f"],
    ["Prompt", "#d2a8ff", "#2a1f4a"],
    ["Schema", "#56d364", "#1f3a20"],
  ].map(([label, stroke, fill]) => `
    <span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;color:var(--text-dim)">
      <svg width="10" height="10"><circle cx="5" cy="5" r="4" fill="${fill}" stroke="${stroke}" stroke-width="1.5"></circle></svg>
      ${label}
    </span>`).join("");

  toolbar.innerHTML = `
    <div class="toolbar-group"><span class="toolbar-label">Store</span><span>${loaded} / ${total} nodes</span></div>
    <div class="toolbar-group">${legend}</div>
    <div class="toolbar-group">
      <button class="toolbar-btn" id="db-fit-btn">Fit</button>
      <button class="toolbar-btn" id="db-reset-btn">Reset</button>
      ${remaining > 0 ? `<button class="toolbar-btn" id="db-load-more-btn">+ ${Math.min(DB_BATCH_SIZE, remaining)} more</button>` : ""}
    </div>
  `;

  document.getElementById("db-fit-btn")?.addEventListener("click", fitDbGraph);
  document.getElementById("db-reset-btn")?.addEventListener("click", resetDbGraph);
  document.getElementById("db-load-more-btn")?.addEventListener("click", loadMoreDbNodes);
}

export function renderDatabaseCanvas() {
  const db = state.graphState;
  if (!db) {
    document.getElementById("db-empty").style.display = "flex";
    document.getElementById("db-toolbar").innerHTML = "";
    return;
  }
  buildDbGraphData();
  dbNodes = dbAllNodes.slice(0, DB_BATCH_SIZE).map((n) => ({ ...n }));
  const loadedIds = new Set(dbNodes.map((n) => n.id));
  dbLinks = dbAllLinks.filter((e) => loadedIds.has(e.source) && loadedIds.has(e.target)).map((e) => ({ ...e }));
  dbSelectedNode = null;
  renderDbSimulation();
  renderDatabaseSidebar();
  dbNeedsRebuild = false;
}

function renderCountChips(counts, className) {
  const entries = Object.entries(counts || {});
  if (!entries.length) return "<div class='empty-panel'>none</div>";
  return entries.map(([name, count]) => `<span class="chip ${className}">${escapeHtml(name)} · ${count}</span>`).join("");
}

export function renderDatabaseSidebar() {
  const container = document.getElementById("tab-database");
  const db = state.graphState;
  if (!db) {
    container.innerHTML = "<div class='empty-panel'>Graph store snapshot not yet received.</div>";
    return;
  }
  const summary = db.summary || {};
  const selected = dbSelectedNode;
  const selectedHtml = selected ? `
    <div class="section-title">Selected Node</div>
    <div class="detail-section">
      <div class="kv-row"><span class="kv-key">name</span><span class="kv-val">${escapeHtml(selected.name || "—")}</span></div>
      <div class="kv-row"><span class="kv-key">type</span><span class="kv-val">${escapeHtml(selected.node_type || "—")}</span></div>
      <div class="kv-row"><span class="kv-key">valid</span><span class="kv-val">${selected.is_valid ? "active" : "expired"}</span></div>
      <div class="kv-row"><span class="kv-key">id</span><span class="kv-val">${escapeHtml(selected.node_id)}</span></div>
      <pre class="json">${prettyJson(selected)}</pre>
    </div>` : "<div class='empty-panel'>Click a node on the database canvas to inspect it.</div>";

  container.innerHTML = `
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-val">${summary.active_node_count || 0}</div><div class="stat-label">Active nodes</div></div>
      <div class="stat-card"><div class="stat-val">${summary.active_edge_count || 0}</div><div class="stat-label">Active edges</div></div>
      <div class="stat-card"><div class="stat-val">${summary.node_count || 0}</div><div class="stat-label">Total nodes</div></div>
      <div class="stat-card"><div class="stat-val">${summary.edge_count || 0}</div><div class="stat-label">Total edges</div></div>
    </div>
    <div class="section-title">Node Types</div>
    <div>${renderCountChips(summary.node_type_counts, "chip-agent")}</div>
    <div class="section-title">Edge Types</div>
    <div>${renderCountChips(summary.edge_type_counts, "chip-tool")}</div>
    ${selectedHtml}
  `;
}

export function renderDatabase() {
  renderDatabaseSidebar();
  if (state.activeTab === "database" && (dbNeedsRebuild || !dbNodes.length)) renderDatabaseCanvas();
}
