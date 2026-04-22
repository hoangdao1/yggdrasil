// Trace-node and edge derivation from an incoming event stream.

import { state } from "./state.js";

export function ingestEvent(event) {
  const nodeId = event.node_id;
  const nodeName = event.node_name || nodeId;
  if (!nodeId) return;

  if (!state.traceNodes.has(nodeId)) {
    state.traceNodes.set(nodeId, {
      id: nodeId,
      name: nodeName,
      type: inferTraceNodeType(event),
      hopOrder: undefined,
      category: "graph",
      refNodeId: nodeId,
    });
  }

  const node = state.traceNodes.get(nodeId);
  node.name = nodeName;
  node.type = inferTraceNodeType(event, node.type);

  if (event.event_type === "hop" && event.payload && event.payload.hop != null) {
    node.hopOrder = event.payload.hop;
  }

  if (event.event_type === "routing") {
    const nextId = event.payload.next_node_id;
    if (nextId && nextId !== "__END__") {
      addTraceEdge("flow", nodeId, nextId, "routing");
      if (!state.traceNodes.has(nextId)) {
        state.traceNodes.set(nextId, {
          id: nextId,
          name: nextId.slice(0, 8),
          type: "agent",
          category: "graph",
          refNodeId: nextId,
        });
      }
    }
  }

  if (event.event_type === "agent_start") {
    const tools = event.payload.tools || [];
    const contexts = event.payload.context || [];
    tools.forEach((name) => {
      const toolId = `tool:${name}`;
      if (!state.traceNodes.has(toolId)) {
        state.traceNodes.set(toolId, {
          id: toolId,
          name,
          type: "tool",
          category: "ephemeral",
          refNodeId: nodeId,
        });
      }
      addTraceEdge("composition", nodeId, toolId, "tool");
    });
    contexts.forEach((name) => {
      const contextId = `context:${name}`;
      if (!state.traceNodes.has(contextId)) {
        state.traceNodes.set(contextId, {
          id: contextId,
          name,
          type: "context",
          category: "ephemeral",
          refNodeId: nodeId,
        });
      }
      addTraceEdge("composition", contextId, nodeId, "context");
    });
  }
}

function inferTraceNodeType(event, existing = "agent") {
  const payloadType = String(event.payload?.node_type || "").toLowerCase();
  if (payloadType.includes("tool")) return "tool";
  if (payloadType.includes("context")) return "context";
  if (payloadType.includes("prompt")) return "prompt";
  if (payloadType.includes("schema")) return "schema";
  if (event.event_type === "tool_call" || event.event_type === "tool_result") return "tool";
  return existing || "agent";
}

function addTraceEdge(lens, source, target, kind) {
  const key = `${source}->${target}`;
  if (!state.traceEdges[lens].has(key)) {
    state.traceEdges[lens].set(key, { source, target, kind });
  }
}
