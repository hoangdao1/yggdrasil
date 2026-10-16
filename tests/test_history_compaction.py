"""Bounded rolling history: shrink old turns in place so a long ReAct loop's context
(re-read every turn) stays bounded, while keeping tool_use/tool_call pairing valid and
the head (task) + most-recent turns full.
"""

from __future__ import annotations

from yggdrasil_lm.core.executor import (
    _HISTORY_ELIDE_CHARS,
    _HISTORY_ELIDE_MARK,
    _clip_for_history,
    _compact_history,
)

BIG = "X" * 5000


def _anthropic_history(pairs: int):
    msgs = [{"role": "user", "content": "TASK " + BIG},
            {"role": "assistant", "content": "setup " + BIG}]
    for i in range(pairs):
        msgs.append({"role": "assistant", "content": [
            {"type": "text", "text": "thinking " + BIG},
            {"type": "tool_use", "id": f"t{i}", "name": "q", "input": {}}]})
        msgs.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"t{i}", "content": "RESULT " + BIG}]})
    return msgs


def test_shrinks_middle_keeps_head_and_recent():
    msgs = _anthropic_history(8)
    before = sum(len(str(m)) for m in msgs)
    _compact_history(msgs)
    after = sum(len(str(m)) for m in msgs)
    assert after < before                                   # shrunk
    assert "TASK " + BIG in str(msgs[0])                    # head kept full
    assert "RESULT " + BIG in str(msgs[-1])                 # most-recent kept full
    assert _HISTORY_ELIDE_MARK in str(msgs)                 # middle elided


def test_preserves_tool_use_blocks_for_pairing():
    msgs = _anthropic_history(8)
    _compact_history(msgs)
    tool_uses = sum(1 for m in msgs for b in (m.get("content") or [])
                    if isinstance(b, dict) and b.get("type") == "tool_use")
    assert tool_uses == 8   # every tool_use survives (else the API rejects the request)


def test_openai_shape_preserves_tool_calls():
    msgs = [{"role": "user", "content": "t"}, {"role": "user", "content": "x"}]
    for i in range(8):
        msgs.append({"role": "assistant", "content": "reason " + BIG,
                     "tool_calls": [{"id": f"c{i}", "type": "function",
                                     "function": {"name": "q", "arguments": "{}"}}]})
        msgs.append({"role": "tool", "tool_call_id": f"c{i}", "content": "RES " + BIG})
    _compact_history(msgs)
    tool_calls = sum(len(m.get("tool_calls", [])) for m in msgs)
    assert tool_calls == 8
    assert _HISTORY_ELIDE_MARK in str(msgs)


def test_idempotent():
    msgs = _anthropic_history(8)
    _compact_history(msgs)
    once = sum(len(str(m)) for m in msgs)
    _compact_history(msgs)
    assert sum(len(str(m)) for m in msgs) == once   # re-running changes nothing


def test_short_history_untouched():
    msgs = _anthropic_history(1)   # 2 head + 2 = 4 msgs, below head+recent threshold
    before = [dict(m) for m in msgs]
    _compact_history(msgs)
    assert msgs == before


def test_clip_only_beyond_budget():
    small = "short text"
    assert _clip_for_history(small) == small
    big = "Y" * (_HISTORY_ELIDE_CHARS + 100)
    clipped = _clip_for_history(big)
    assert _HISTORY_ELIDE_MARK in clipped and len(clipped) < len(big)
