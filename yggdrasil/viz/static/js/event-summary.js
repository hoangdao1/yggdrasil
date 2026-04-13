// Short, human-readable summary strings for each event type.

import { nodeNameForId } from "./state.js";

export function eventSummary(event) {
  const payload = event.payload || {};
  switch (event.event_type) {
    case "hop":
      return `hop ${payload.hop != null ? payload.hop : "?"} · ${String(payload.node_type || "").split(".").pop()}`;
    case "agent_start":
      return `${event.node_name} [${payload.model || "?"}] · ${(payload.tools || []).length} tools · ${(payload.context || []).length} context`;
    case "agent_end":
      return `intent=${payload.intent || "default"} · ${payload.iterations || 1} iter`;
    case "tool_call":
      return payload.callable_ref || event.node_name;
    case "tool_result":
      return `${payload.success === false ? "error" : "ok"} · ${(payload.output_summary || "").slice(0, 80)}`;
    case "context_inject":
      return `${payload.count || 0} context nodes`;
    case "routing":
      return `${payload.intent || "default"} -> ${nodeNameForId(payload.next_node_id)}`;
    case "pause":
      return `${payload.reason || "workflow paused"}${payload.waiting_for ? ` · waiting for ${payload.waiting_for}` : ""}`;
    case "resume":
      return `resumed${payload.waiting_for ? ` from ${payload.waiting_for}` : ""}`;
    case "retry":
      return `attempt ${payload.attempt || "?"}/${payload.max_attempts || "?"} · ${payload.error || ""}`;
    case "validation":
      return payload.success === false ? `validation failed · ${payload.error || ""}` : "validation passed";
    case "permission_denied":
      return payload.error || "permission denied";
    case "checkpoint":
      return `checkpoint ${String(payload.checkpoint_node_id || "").slice(0, 8)}`;
    case "approval_task":
      return `task ${String(payload.task_id || "").slice(0, 8)} · ${(payload.assignees || []).join(", ") || "unassigned"}`;
    case "lease":
      return `${payload.resource_id || "resource"} -> ${payload.owner || "owner"}`;
    case "schedule":
      return `${payload.run_at || payload.due_at || "scheduled"}${payload.owner ? ` · ${payload.owner}` : ""}`;
    case "migration":
      return `${payload.from_version || "?"} -> ${payload.to_version || "?"}`;
    case "error":
      return `${payload.error_type || "Error"}: ${payload.error || "unknown error"}`;
    default:
      return event.event_type;
  }
}
