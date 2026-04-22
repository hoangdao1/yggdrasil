// Pure helpers and constants. No DOM, no state access.

export const EVENT_LABELS = {
  hop: "Hop",
  agent_start: "Agent Start",
  agent_end: "Agent End",
  tool_call: "Tool Call",
  tool_result: "Tool Result",
  context_inject: "Context",
  routing: "Routing",
  validation: "Validation",
  subgraph_enter: "Subgraph In",
  subgraph_exit: "Subgraph Out",
  pause: "Pause",
  resume: "Resume",
  retry: "Retry",
  permission_denied: "Permission",
  checkpoint: "Checkpoint",
  transaction: "Transaction",
  approval_task: "Approval",
  lease: "Lease",
  schedule: "Schedule",
  migration: "Migration",
  error: "Fatal Error",
};

export const EVENT_FILTER_ORDER = [
  "hop",
  "agent_start",
  "agent_end",
  "tool_call",
  "tool_result",
  "context_inject",
  "routing",
  "validation",
  "pause",
  "resume",
  "retry",
  "permission_denied",
  "checkpoint",
  "approval_task",
  "lease",
  "schedule",
  "migration",
  "error",
];

export const RUNTIME_EVENT_TYPES = new Set([
  "pause",
  "resume",
  "retry",
  "validation",
  "permission_denied",
  "checkpoint",
  "transaction",
  "approval_task",
  "lease",
  "schedule",
  "migration",
]);

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function prettyJson(value) {
  return escapeHtml(JSON.stringify(value, null, 2));
}

// Tagged template: `html\`<div>${userInput}</div>\`` — auto-escapes interpolations.
// Use `html.raw(str)` to opt out of escaping for pre-built markup.
export function html(strings, ...values) {
  let out = "";
  for (let i = 0; i < strings.length; i += 1) {
    out += strings[i];
    if (i < values.length) out += renderValue(values[i]);
  }
  return out;
}

function renderValue(value) {
  if (value == null || value === false) return "";
  if (Array.isArray(value)) return value.map(renderValue).join("");
  if (typeof value === "object" && value.__raw) return value.value;
  return escapeHtml(value);
}

html.raw = (value) => ({ __raw: true, value: value == null ? "" : String(value) });

export function eventLabel(type) {
  return EVENT_LABELS[type] || type;
}

export function eventTypeClass(type) {
  return `type-${type}`;
}

export function isErrorEvent(event) {
  const payload = event.payload || {};
  return (
    event.event_type === "error" ||
    event.event_type === "permission_denied" ||
    event.event_type === "retry" ||
    (event.event_type === "tool_result" && payload.success === false) ||
    (event.event_type === "validation" && payload.success === false)
  );
}

export function isRuntimeEvent(event) {
  return RUNTIME_EVENT_TYPES.has(event.event_type);
}

export function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).catch(() => {});
  }
}

export function tsOf(event) {
  if (event && event.timestamp) {
    const parsed = new Date(event.timestamp).getTime();
    if (!Number.isNaN(parsed)) return parsed;
  }
  return Date.now();
}

export function fmtElapsed(ms) {
  const s = Math.max(0, Math.floor(ms / 1000));
  const mm = String(Math.floor(s / 60)).padStart(2, "0");
  const ss = String(s % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

export function fmtDurationMs(ms) {
  if (ms == null) return "";
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${m}m${s.toString().padStart(2, "0")}s`;
}

export function nodeColor(type) {
  const normalized = String(type || "").toLowerCase();
  if (normalized.includes("tool")) return "#4a3000";
  if (normalized.includes("context")) return "#003b4f";
  if (normalized.includes("prompt")) return "#2a1f4a";
  if (normalized.includes("schema")) return "#1f3a20";
  return "#1f4068";
}

export function nodeStroke(type) {
  const normalized = String(type || "").toLowerCase();
  if (normalized.includes("tool")) return "#e3b341";
  if (normalized.includes("context")) return "#58a6ff";
  if (normalized.includes("prompt")) return "#d2a8ff";
  if (normalized.includes("schema")) return "#56d364";
  return "#79c0ff";
}
