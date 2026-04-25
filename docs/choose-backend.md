# Choose a Backend

`yggdrasil` separates orchestration from model providers.

## Fast Rule Of Thumb

- Use `provider="anthropic"` if you want the default hosted path
- Use `provider="claude-code"` if you want local Claude Code sub-agents authenticated
  through your Claude Code CLI session
- Use `provider="compatible"` for OpenAI-compatible APIs, including OpenAI itself
- Pass `backend=...` directly when you need full control

## Builder API

Anthropic:

```python
from yggdrasil import GraphApp

app = GraphApp(provider="anthropic", api_key="sk-ant-...")
```

Compatible hosted API:

```python
from yggdrasil import GraphApp

app = GraphApp(
    provider="compatible",
    api_key="sk-...",
)
```

Local compatible server:

```python
from yggdrasil import GraphApp

app = GraphApp(
    provider="compatible",
    # `provider="openai"` still works as a compatibility alias.
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
```

Claude Code executor:

```python
from yggdrasil import GraphApp

app = GraphApp(
    provider="claude-code",
    cwd="/path/to/project",
    permission_mode="acceptEdits",
)
```

This path uses `ClaudeCodeExecutor`: each `AgentNode` runs as a Claude Code
sub-agent, and graph `ToolNode`s can be bridged into the sub-agent as in-process
MCP tools. It does not require `ANTHROPIC_API_KEY` just to construct the
executor; routing uses the local `claude` CLI when available.

## Low-Level API

```python
from yggdrasil import ClaudeCodeExecutor, GraphExecutor, OpenAIBackend

executor = GraphExecutor(
    store,
    backend=OpenAIBackend(base_url="http://localhost:11434/v1", api_key="ollama"),
)

claude_code_executor = ClaudeCodeExecutor(store, cwd="/path/to/project")
```

## Why This Split Exists

The runtime should not force a single model provider. The builder API is there to make setup discoverable, while the low-level backend classes still expose full control.
