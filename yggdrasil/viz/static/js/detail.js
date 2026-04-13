// Per-event detail renderer — used inline inside the events tab drawer.

import { html, escapeHtml, prettyJson, eventTypeClass, eventLabel } from "./format.js";
import { eventSummary } from "./event-summary.js";
import { state, nodeNameForId } from "./state.js";

export function renderDetailHtml(event) {
  if (!event) return "<div class='empty-panel'>Select an event to inspect it.</div>";
  const payload = event.payload || {};
  const relations = relatedEvents(event);
  const currentNode = state.traceNodes.get(event.node_id);

  let out = html`
    <div class="detail-actions">
      <button class="copy-btn" data-copy="event" data-event-id="${event.event_id}">Copy event JSON</button>
      <button class="copy-btn" data-copy="payload" data-event-id="${event.event_id}">Copy payload JSON</button>
    </div>

    <div class="detail-section">
      <div class="detail-label">What happened</div>
      <div class="kv-row"><span class="kv-key">event</span><span class="kv-val ${eventTypeClass(event.event_type)}">${eventLabel(event.event_type)}</span></div>
      <div class="kv-row"><span class="kv-key">node</span><span class="kv-val">${event.node_name || event.node_id}</span></div>
      <div class="kv-row"><span class="kv-key">summary</span><span class="kv-val">${eventSummary(event)}</span></div>
      ${event.duration_ms != null ? html.raw(`<div class="kv-row"><span class="kv-key">duration</span><span class="kv-val">${event.duration_ms}ms</span></div>`) : ""}
      <div class="kv-row"><span class="kv-key">time</span><span class="kv-val">${event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ""}</span></div>
      ${currentNode ? html.raw(`<div class="kv-row"><span class="kv-key">graph node</span><span class="kv-val">${escapeHtml(currentNode.type)}</span></div>`) : ""}
    </div>
  `;

  out += renderTypeSpecificDetail(event);

  const navLinks = [];
  if (relations.parent) {
    navLinks.push(`<span class="nav-link" data-jump="${escapeHtml(relations.parent.event_id)}">Parent: ${escapeHtml(eventLabel(relations.parent.event_type))}</span>`);
  }
  for (const child of relations.children) {
    navLinks.push(`<span class="nav-link" data-jump="${escapeHtml(child.event_id)}">Child: ${escapeHtml(eventLabel(child.event_type))}</span>`);
  }
  const sameNodeLinks = relations.sameNode.map((r) =>
    `<span class="nav-link" data-jump="${escapeHtml(r.event_id)}">${escapeHtml(eventLabel(r.event_type))}</span>`
  ).join("");

  out += `
    <div class="detail-section">
      <div class="detail-label">Navigation</div>
      <div class="nav-row">${navLinks.join("")}</div>
      ${relations.sameNode.length ? `<div class="detail-label" style="margin-top:10px">Related events for this node</div><div class="nav-row">${sameNodeLinks}</div>` : ""}
    </div>
    <div class="detail-section">
      <details>
        <summary>Raw payload</summary>
        <pre class="json">${prettyJson(payload)}</pre>
      </details>
    </div>
  `;

  return out;
}

export function bindDetailHandlers(container) {
  container.querySelectorAll("[data-jump]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      window.dispatchEvent(new CustomEvent("viz:select-event", { detail: { eventId: el.dataset.jump } }));
    });
  });
  container.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", (e) => {
      e.stopPropagation();
      const mode = button.dataset.copy;
      const ev = state.eventIndex.get(button.dataset.eventId);
      if (!ev) return;
      const text = mode === "payload"
        ? JSON.stringify(ev.payload || {}, null, 2)
        : JSON.stringify(ev, null, 2);
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(() => {});
      }
    });
  });
}

function relatedEvents(event) {
  return {
    parent: event.parent_event_id ? state.eventIndex.get(event.parent_event_id) : null,
    children: state.events.filter((c) => c.parent_event_id === event.event_id),
    sameNode: state.events.filter((c) => c.node_id === event.node_id && c.event_id !== event.event_id).slice(-5),
  };
}

function renderTypeSpecificDetail(event) {
  const payload = event.payload || {};

  if (event.event_type === "agent_start") {
    const scores = payload.context_scores || [];
    return `
      <div class="detail-section">
        <div class="detail-label">Why this agent ran</div>
        <div class="kv-row"><span class="kv-key">model</span><span class="kv-val">${escapeHtml(payload.model || "?")}</span></div>
        <div class="kv-row"><span class="kv-key">tools</span><span class="kv-val">${escapeHtml((payload.tools || []).join(", ") || "none")}</span></div>
        <div class="kv-row"><span class="kv-key">context</span><span class="kv-val">${escapeHtml((payload.context || []).join(", ") || "none")}</span></div>
      </div>
      ${scores.length ? `<div class="detail-section"><div class="detail-label">Context scores</div>${scores.map(renderContextScoreCard).join("")}</div>` : ""}
    `;
  }

  if (event.event_type === "context_inject") {
    const selected = payload.selected_contexts || [];
    return `
      <div class="detail-section">
        <div class="detail-label">Selected context</div>
        ${selected.length ? selected.map(renderContextScoreCard).join("") : `<div class="kv-val">${escapeHtml((payload.context_names || []).join(", ") || "none")}</div>`}
      </div>
    `;
  }

  if (event.event_type === "tool_call") {
    return `
      <div class="detail-section">
        <div class="detail-label">Tool call</div>
        <div class="kv-row"><span class="kv-key">callable</span><span class="kv-val">${escapeHtml(payload.callable_ref || "?")}</span></div>
        <div class="detail-label" style="margin-top:8px">Input</div>
        <pre class="json">${prettyJson(payload.input || {})}</pre>
      </div>
    `;
  }

  if (event.event_type === "tool_result") {
    const ok = payload.success !== false;
    return `
      <div class="detail-section">
        <div class="detail-label">Result</div>
        <div class="kv-row"><span class="kv-key">status</span><span class="kv-val" style="color:${ok ? "var(--green)" : "var(--red)"}">${ok ? "success" : "error"}</span></div>
        <div class="kv-row"><span class="kv-key">impact</span><span class="kv-val">${ok ? "Tool completed." : "Tool failed and may have affected later routing or output."}</span></div>
        <div class="detail-label" style="margin-top:8px">Output</div>
        <pre class="json">${escapeHtml((payload.output_summary || "").slice(0, 2000))}</pre>
      </div>
    `;
  }

  if (event.event_type === "routing") {
    const confidence = payload.confidence;
    return `
      <div class="detail-section">
        <div class="detail-label">Routing decision</div>
        <div class="kv-row"><span class="kv-key">intent</span><span class="kv-val">${escapeHtml(payload.intent || "default")}</span></div>
        <div class="kv-row"><span class="kv-key">next</span><span class="kv-val">${escapeHtml(nodeNameForId(payload.next_node_id))}</span></div>
        <div class="kv-row"><span class="kv-key">mode</span><span class="kv-val">${escapeHtml(payload.mode || "llm")}</span></div>
        ${confidence != null ? `<div class="kv-row"><span class="kv-key">confidence</span><span class="kv-val" style="color:${confidence < 0.7 ? "var(--yellow)" : "var(--green)"}">${(confidence * 100).toFixed(0)}%</span></div>` : ""}
        ${payload.reason ? `<div class="kv-row"><span class="kv-key">why</span><span class="kv-val">${escapeHtml(payload.reason)}</span></div>` : ""}
      </div>
    `;
  }

  if (event.event_type === "pause") {
    return `
      <div class="detail-section">
        <div class="detail-label">Workflow state</div>
        <div class="kv-row"><span class="kv-key">reason</span><span class="kv-val">${escapeHtml(payload.reason || "paused")}</span></div>
        <div class="kv-row"><span class="kv-key">waiting for</span><span class="kv-val">${escapeHtml(payload.waiting_for || "external input")}</span></div>
        <div class="kv-row"><span class="kv-key">token</span><span class="kv-val">${escapeHtml(payload.token || "")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "resume") {
    return `
      <div class="detail-section">
        <div class="detail-label">Workflow resumed</div>
        <div class="kv-row"><span class="kv-key">token</span><span class="kv-val">${escapeHtml(payload.token || "")}</span></div>
        <div class="kv-row"><span class="kv-key">waiting for</span><span class="kv-val">${escapeHtml(payload.waiting_for || "n/a")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "retry") {
    return `
      <div class="detail-section">
        <div class="detail-label">Retry information</div>
        <div class="kv-row"><span class="kv-key">attempt</span><span class="kv-val">${payload.attempt || "?"} / ${payload.max_attempts || "?"}</span></div>
        <div class="kv-row"><span class="kv-key">error</span><span class="kv-val">${escapeHtml(payload.error || "")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "validation") {
    return `
      <div class="detail-section">
        <div class="detail-label">Validation</div>
        <div class="kv-row"><span class="kv-key">status</span><span class="kv-val" style="color:${payload.success === false ? "var(--red)" : "var(--green)"}">${payload.success === false ? "failed" : "passed"}</span></div>
        ${payload.error ? `<div class="kv-row"><span class="kv-key">error</span><span class="kv-val">${escapeHtml(payload.error)}</span></div>` : ""}
      </div>
    `;
  }

  if (event.event_type === "permission_denied") {
    return `
      <div class="detail-section">
        <div class="detail-label">Permission denied</div>
        <div class="kv-row"><span class="kv-key">impact</span><span class="kv-val">Execution was blocked by a guardrail.</span></div>
        <div class="kv-row"><span class="kv-key">error</span><span class="kv-val">${escapeHtml(payload.error || "")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "checkpoint") {
    return `
      <div class="detail-section">
        <div class="detail-label">Checkpoint</div>
        <div class="kv-row"><span class="kv-key">node</span><span class="kv-val">${escapeHtml(payload.checkpoint_node_id || "")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "approval_task") {
    return `
      <div class="detail-section">
        <div class="detail-label">Approval task</div>
        <div class="kv-row"><span class="kv-key">task</span><span class="kv-val">${escapeHtml(payload.task_id || "")}</span></div>
        <div class="kv-row"><span class="kv-key">assignees</span><span class="kv-val">${escapeHtml((payload.assignees || []).join(", ") || "none")}</span></div>
        <div class="kv-row"><span class="kv-key">assigned</span><span class="kv-val">${escapeHtml(payload.assigned_to || "unassigned")}</span></div>
        <div class="kv-row"><span class="kv-key">due</span><span class="kv-val">${escapeHtml(payload.due_at || "n/a")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "lease") {
    return `
      <div class="detail-section">
        <div class="detail-label">Lease</div>
        <div class="kv-row"><span class="kv-key">resource</span><span class="kv-val">${escapeHtml(payload.resource_id || "")}</span></div>
        <div class="kv-row"><span class="kv-key">owner</span><span class="kv-val">${escapeHtml(payload.owner || "")}</span></div>
        <div class="kv-row"><span class="kv-key">expires</span><span class="kv-val">${escapeHtml(payload.expires_at || "")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "schedule") {
    return `
      <div class="detail-section">
        <div class="detail-label">Scheduled resume</div>
        <div class="kv-row"><span class="kv-key">run at</span><span class="kv-val">${escapeHtml(payload.run_at || payload.due_at || "")}</span></div>
        ${payload.task_id ? `<div class="kv-row"><span class="kv-key">task</span><span class="kv-val">${escapeHtml(payload.task_id)}</span></div>` : ""}
      </div>
    `;
  }

  if (event.event_type === "migration") {
    return `
      <div class="detail-section">
        <div class="detail-label">Migration</div>
        <div class="kv-row"><span class="kv-key">from</span><span class="kv-val">${escapeHtml(payload.from_version || "")}</span></div>
        <div class="kv-row"><span class="kv-key">to</span><span class="kv-val">${escapeHtml(payload.to_version || "")}</span></div>
      </div>
    `;
  }

  if (event.event_type === "error") {
    return `
      <div class="detail-section">
        <div class="detail-label">Fatal Error</div>
        <div class="kv-row"><span class="kv-key">type</span><span class="kv-val" style="color:var(--red)">${escapeHtml(payload.error_type || "Error")}</span></div>
        <div class="kv-row"><span class="kv-key">message</span><span class="kv-val">${escapeHtml(payload.error || "")}</span></div>
      </div>
    `;
  }

  return "";
}

function renderContextScoreCard(score) {
  const numeric = Number(score.score || 0);
  return `
    <div class="context-card">
      <div class="context-name">${escapeHtml(score.name || "context")}</div>
      <div class="score-bar-wrap">
        <div class="score-bar"><div class="score-bar-fill" style="width:${Math.round(numeric * 100)}%"></div></div>
        <div class="score-val">${numeric.toFixed(3)}</div>
      </div>
      <div class="event-meta">source=${escapeHtml(score.source || "?")} · hops=${escapeHtml(score.hops || 0)}${score.token_count != null ? ` · tokens=${escapeHtml(score.token_count)}` : ""}</div>
      ${(score.reasons || []).length ? `<div class="event-meta">reasons: ${escapeHtml(score.reasons.join(", "))}</div>` : ""}
    </div>
  `;
}
