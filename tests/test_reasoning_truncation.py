"""Reasoning-model turn handling: max_tokens truncation escalation + reasoning salvage.

Covers the executor no longer mistaking a token-truncated, empty turn for a completed
one (it retries with a larger budget, bounded), and the OpenAI backend surfacing
`reasoning_content` + a distinct `max_tokens` stop reason.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.backends.llm import OpenAIBackend
from yggdrasil_lm.testing import StubBackend, end_turn, max_tokens_truncated

EXPECTED_MAX_TOKENS = 12345  # sentinel max_tokens forwarded to the backend
TWO_BACKEND_CALLS = 2        # initial turn + one retry/nudge
THREE_BACKEND_CALLS = 3      # initial turn + two bounded retries/escalations
FOUR_BACKEND_CALLS = 4       # initial turn + three bounded corrections

# ---------------------------------------------------------------------------
# OpenAI backend: finish_reason mapping + reasoning capture
# ---------------------------------------------------------------------------

def _fake_openai_response(*, content, finish_reason, reasoning=None, tool_calls=None):
    msg = SimpleNamespace(content=content, reasoning_content=reasoning, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg, finish_reason=finish_reason)])


def _backend_returning(resp):
    backend = OpenAIBackend(base_url="http://localhost:0/v1", api_key="test")

    async def _create(**kwargs):
        _backend_returning.last_kwargs = kwargs
        return resp

    backend._client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=_create)))
    return backend


@pytest.mark.asyncio
async def test_openai_length_becomes_max_tokens_and_captures_reasoning():
    """A `length` finish with only reasoning_content → stop_reason 'max_tokens', text ''."""
    resp = _fake_openai_response(content=None, finish_reason="length", reasoning="thinking " * 100)
    backend = _backend_returning(resp)

    out = await backend.chat(model="m", system="s", messages=[{"role": "user", "content": "go"}], tools=[])

    assert out.stop_reason == "max_tokens"
    assert out.text == ""
    assert out.reasoning.startswith("thinking ")
    assert out.tool_calls == []


@pytest.mark.asyncio
async def test_openai_tool_calls_and_stop_map_correctly():
    tc = SimpleNamespace(id="c1", function=SimpleNamespace(name="do", arguments="{}"))
    tool_resp = _fake_openai_response(content="", finish_reason="tool_calls", tool_calls=[tc])
    stop_resp = _fake_openai_response(content="done", finish_reason="stop")

    b1 = _backend_returning(tool_resp)
    out1 = await b1.chat(model="m", system="s", messages=[{"role": "user", "content": "x"}], tools=[])
    assert out1.stop_reason == "tool_use"
    assert [t.name for t in out1.tool_calls] == ["do"]

    b2 = _backend_returning(stop_resp)
    out2 = await b2.chat(model="m", system="s", messages=[{"role": "user", "content": "x"}], tools=[])
    assert out2.stop_reason == "end_turn"
    assert out2.text == "done"


@pytest.mark.asyncio
async def test_openai_forwards_max_tokens():
    resp = _fake_openai_response(content="ok", finish_reason="stop")
    backend = _backend_returning(resp)
    await backend.chat(model="m", system="s", messages=[{"role": "user", "content": "x"}], tools=[], max_tokens=12345)
    assert _backend_returning.last_kwargs["max_tokens"] == EXPECTED_MAX_TOKENS


# ---------------------------------------------------------------------------
# Executor: escalation on empty truncation, then completion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_truncated_empty_turn_escalates_then_completes():
    """A max_tokens turn with no output must NOT end the agent: retry with more room."""
    backend = StubBackend([
        max_tokens_truncated(reasoning="reasoning ate the whole budget"),
        end_turn("DONE"),
    ])
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    # Completed with the real answer, not an empty result.
    assert ctx.outputs[sub.node_id]["text"] == "DONE"
    # Two turns; the second ran with an escalated (doubled) token budget.
    assert len(backend.max_tokens_seen) == TWO_BACKEND_CALLS
    assert backend.max_tokens_seen[1] == backend.max_tokens_seen[0] * 2


@pytest.mark.asyncio
async def test_persistent_truncation_gives_up_bounded_and_salvages_reasoning():
    """If every turn truncates, escalation is bounded and reasoning is salvaged as text."""
    backend = StubBackend(lambda *a: max_tokens_truncated(reasoning="all in the head"))
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    # Bounded: initial call + 2 escalations = 3 chat calls, then terminate (not max_iterations=10).
    assert len(backend.max_tokens_seen) == THREE_BACKEND_CALLS
    assert backend.max_tokens_seen == [8096, 16192, 32000]
    # Never surfaces an empty result — the chain-of-thought is salvaged.
    assert ctx.outputs[sub.node_id]["text"] == "all in the head"


@pytest.mark.asyncio
async def test_end_turn_empty_text_salvages_reasoning():
    """A natural end_turn with empty content still returns the reasoning, never ''."""
    backend = StubBackend([end_turn("", reasoning="the visible answer lived in reasoning")])
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    assert ctx.outputs[sub.node_id]["text"] == "the visible answer lived in reasoning"


# ---------------------------------------------------------------------------
# Unparsed tool calls: a local model writing a tool call as TEXT
#
# When the server's tool-call parser doesn't recognise the model's format (or the
# model blends two conventions), the markup is left in `content` and `tool_calls`
# is empty. The turn then looks like a finished answer while having done no work —
# which ended pipeline steps mid-task with none of their outputs written.
# ---------------------------------------------------------------------------

# Verbatim from prism-ml/bonsai-27b: a Hermes <tool_call> wrapper around a
# Llama-style <function=…><parameter=…> body — neither convention, so unparsed.
_BLENDED_MARKUP = """: build-weekly-report, step 3 of 9.

<tool_call>
<function=get_step_status>
<parameter=step_id>
load_inventory_levels
</parameter>
</function>
</tool_call>"""


@pytest.mark.parametrize("text", [
    _BLENDED_MARKUP,
    '<tool_call>{"name": "get_catalog", "arguments": {}}</tool_call>',   # Hermes / Qwen
    "<function=get_catalog>{}</function>",                              # Llama 3 / functionary
    "<function_call>get_catalog</function_call>",
    '<|tool_call|>{"name": "x"}',                                    # ChatML sentinel
    '<invoke name="get_catalog">',                                      # Anthropic-XML imitation
])
def test_detects_unparsed_tool_call_formats(text):
    from yggdrasil_lm.backends.llm import looks_like_unparsed_tool_call
    assert looks_like_unparsed_tool_call(text)


@pytest.mark.parametrize("text", [
    "",
    "The catalog has 12 top-level categories and no clearance section.",
    "I called get_catalog and it returned 206 items.",          # merely mentions a tool
    "Use the tool_call field, not prose.",                   # mentions the concept
    "Comparing a < b and c > d gives the ordering.",          # stray angle brackets
])
def test_plain_text_is_not_mistaken_for_a_tool_call(text):
    from yggdrasil_lm.backends.llm import looks_like_unparsed_tool_call
    assert not looks_like_unparsed_tool_call(text)


@pytest.mark.asyncio
async def test_openai_RECOVERS_a_tool_call_written_as_text():
    """Markup the server left as text is PARSED into a real call — the turn's work is
    kept instead of spending a turn asking the model to try again (which it often
    cannot do). Only unparseable markup falls back to the re-prompt."""
    resp = _fake_openai_response(content=_BLENDED_MARKUP, finish_reason="stop")
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "go"}],
        tools=[{"name": "get_step_status", "description": "d", "input_schema": {"type": "object"}}],
    )

    assert out.stop_reason == "tool_use"
    assert [c.name for c in out.tool_calls] == ["get_step_status"]
    assert out.tool_calls[0].input == {"step_id": "load_inventory_levels"}


@pytest.mark.asyncio
async def test_unparseable_markup_still_falls_back_to_a_reprompt():
    """An opening tag with no recoverable name/arguments keeps the old behaviour."""
    resp = _fake_openai_response(content="<tool_call>\n(garbled", finish_reason="stop")
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "go"}],
        tools=[{"name": "t", "description": "d", "input_schema": {"type": "object"}}])

    assert out.stop_reason == "unparsed_tool_call"
    assert out.tool_calls == []


@pytest.mark.asyncio
async def test_no_tools_offered_means_markup_is_just_text():
    """With no tools available the model cannot be calling one — stays a normal end_turn."""
    resp = _fake_openai_response(content=_BLENDED_MARKUP, finish_reason="stop")
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "go"}], tools=[])

    assert out.stop_reason == "end_turn"


@pytest.mark.asyncio
async def test_real_tool_call_is_never_flagged():
    """A turn that DID produce a structured call is untouched even if content has markup."""
    tc = SimpleNamespace(id="c1", function=SimpleNamespace(name="do", arguments="{}"))
    resp = _fake_openai_response(content=_BLENDED_MARKUP, finish_reason="tool_calls", tool_calls=[tc])
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "x"}],
        tools=[{"name": "do", "description": "d", "input_schema": {"type": "object"}}])

    assert out.stop_reason == "tool_use"
    assert [t.name for t in out.tool_calls] == ["do"]


# ── executor recovery ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unparsed_tool_call_is_corrected_then_agent_continues():
    """The markup turn must NOT end the agent — it gets a correction and carries on."""
    from yggdrasil_lm.testing import unparsed_tool_call
    backend = StubBackend([
        unparsed_tool_call(_BLENDED_MARKUP),
        end_turn("DONE"),
    ])
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    # The real answer, not the raw markup.
    assert ctx.outputs[sub.node_id]["text"] == "DONE"
    assert len(backend.calls) == TWO_BACKEND_CALLS
    # The second turn was told its call had not run.
    second_turn_messages = backend.calls[1][2]
    assert any("was NOT executed" in str(m.get("content", "")) for m in second_turn_messages)


@pytest.mark.asyncio
async def test_persistent_unparsed_tool_calls_terminate_bounded():
    """A model that never produces a well-formed call still stops — no infinite loop."""
    from yggdrasil_lm.testing import unparsed_tool_call
    backend = StubBackend(lambda *a: unparsed_tool_call(_BLENDED_MARKUP))
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    # initial turn + 3 bounded corrections, then terminal — not max_iterations.
    assert len(backend.calls) == FOUR_BACKEND_CALLS
    # The markup is still surfaced as the result rather than an empty string, so a
    # downstream done-criteria check reports what the model actually produced.
    assert "get_step_status" in ctx.outputs[sub.node_id]["text"]


# ── the markup arrives in the REASONING channel ──────────────────────────────
# The case that actually occurred in production: bonsai-27b returned content="\n\n"
# and put the hybrid tool-call markup in `reasoning_content`. A detector that only
# looked at `content` saw an empty string, so the turn was accepted as a final answer
# and the step ended having written none of its outputs.

@pytest.mark.asyncio
async def test_tool_call_recovered_from_the_reasoning_channel():
    """The production shape: content is "\n\n" and the call is in reasoning_content."""
    resp = _fake_openai_response(content="\n\n", finish_reason="stop", reasoning=_BLENDED_MARKUP)
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "go"}],
        tools=[{"name": "get_step_status", "description": "d", "input_schema": {"type": "object"}}])

    assert out.stop_reason == "tool_use"
    assert [c.name for c in out.tool_calls] == ["get_step_status"]


@pytest.mark.asyncio
async def test_clean_reasoning_with_empty_content_is_still_a_normal_end_turn():
    """Ordinary chain-of-thought must not be mistaken for an unparsed call."""
    resp = _fake_openai_response(
        content="", finish_reason="stop",
        reasoning="I have all the information I need; the catalog has no clearance section.")
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "go"}],
        tools=[{"name": "t", "description": "d", "input_schema": {"type": "object"}}])

    assert out.stop_reason == "end_turn"


def test_detector_accepts_multiple_channels():
    from yggdrasil_lm.backends.llm import looks_like_unparsed_tool_call
    # in either position, and tolerant of None
    assert looks_like_unparsed_tool_call("", _BLENDED_MARKUP)
    assert looks_like_unparsed_tool_call(_BLENDED_MARKUP, "")
    assert looks_like_unparsed_tool_call(None, _BLENDED_MARKUP)
    assert not looks_like_unparsed_tool_call(None, None)
    assert not looks_like_unparsed_tool_call("", "")
    assert not looks_like_unparsed_tool_call("just prose", "more prose")


# ── recovering the call outright (S8) + rejecting server-mangled args (S7) ───

from yggdrasil_lm.backends.llm import (
    ToolCall as _TC,
    has_mangled_tool_args,
    parse_text_tool_calls,
)


def test_parses_the_blended_hybrid():
    calls = parse_text_tool_calls(_BLENDED_MARKUP)
    assert [c.name for c in calls] == ["get_step_status"]
    assert calls[0].input == {"step_id": "load_inventory_levels"}


def test_parses_hermes_json_body():
    calls = parse_text_tool_calls(
        '<tool_call>{"name": "get_rules", "arguments": {"include_code": true}}</tool_call>')
    assert calls[0].name == "get_rules"
    assert calls[0].input == {"include_code": True}


def test_parses_hermes_with_stringified_arguments():
    calls = parse_text_tool_calls(
        '<tool_call>{"name": "f", "arguments": "{\\"a\\": 1}"}</tool_call>')
    assert calls[0].input == {"a": 1}


def test_parses_plain_llama_dialect_with_several_params():
    calls = parse_text_tool_calls(
        "<function=query>"
        "<parameter=alias>product_type</parameter>"
        "<parameter=limit>5</parameter>"
        "</function>")
    assert calls[0].name == "query"
    assert calls[0].input == {"alias": "product_type", "limit": "5"}


def test_parses_two_calls_without_cross_assigning_params():
    calls = parse_text_tool_calls(
        "<function=a><parameter=x>1</parameter></function>"
        "<function=b><parameter=y>2</parameter></function>")
    assert [(c.name, c.input) for c in calls] == [("a", {"x": "1"}), ("b", {"y": "2"})]


def test_parses_from_either_channel():
    assert parse_text_tool_calls(None, _BLENDED_MARKUP)[0].name == "get_step_status"
    assert parse_text_tool_calls("", "")  == []
    assert parse_text_tool_calls(None, None) == []


@pytest.mark.parametrize("text", [
    "no markup here at all",
    "<tool_call>(truncated",                       # opening tag, nothing recoverable
    "<tool_call>{not json}</tool_call>",
])
def test_unrecoverable_text_yields_no_calls(text):
    assert parse_text_tool_calls(text) == []


def test_detects_server_mangled_argument_keys():
    """Verbatim from LM Studio: an XML call half-parsed into markup-fragment keys."""
    mangled = _TC(id="c1", name="search_examples", input={
        "tags\n</parameter": "<parameter=limit>\n5",
        "keywords\n</parameter": "<parameter=regions",
    })
    assert has_mangled_tool_args([mangled])


def test_clean_arguments_are_not_flagged_as_mangled():
    assert not has_mangled_tool_args([_TC(id="c", name="f", input={"tags": ["new"]})])
    assert not has_mangled_tool_args([_TC(id="c", name="f", input={})])
    assert not has_mangled_tool_args([])
    # a non-dict input must not crash the check
    assert not has_mangled_tool_args([_TC(id="c", name="f", input=None)])


@pytest.mark.asyncio
async def test_mangled_call_is_not_executed_with_lost_arguments():
    """The regression: the call 'succeeded' with every real argument dropped, so the
    tool silently answered a different question. A wrong answer is worse than a failure."""
    tc = SimpleNamespace(id="c1", function=SimpleNamespace(
        name="search_examples",
        arguments='{"tags\\n</parameter": "<parameter=limit>\\n5"}'))
    resp = _fake_openai_response(content="", finish_reason="tool_calls", tool_calls=[tc])
    backend = _backend_returning(resp)

    out = await backend.chat(
        model="m", system="s", messages=[{"role": "user", "content": "x"}],
        tools=[{"name": "search_examples", "description": "d",
                "input_schema": {"type": "object"}}])

    assert out.stop_reason == "unparsed_tool_call"
    assert out.tool_calls == []


# ── narration-only turns are not answers (S4) ────────────────────────────────
# Measured on run df80a65a: four aggregator shards ended at 12/23/5/12 of a 100-turn
# budget having written nothing, their final text either "\n\n" or exactly a lead-in
# like "Now let me resolve all the input field contexts for these targets:". The model
# was announcing its next action; the loop accepted it as the answer.

from yggdrasil_lm.core.executor import looks_like_narration_only


@pytest.mark.parametrize("text", [
    "",
    "   ",
    "\n\n",                                                       # shard 1 / shard 2
    "\n\nNow let me resolve all the input field contexts for these targets:\n\n",  # shard 0
    "\n\nNow let me resolve all field contexts in one batch call:\n\n",            # shard 3
    "Let me read the input slice:",
    "Next, I'll reconcile the remaining targets:",
    "I will now write the shard output:",
])
def test_announcements_and_blanks_are_not_answers(text):
    assert looks_like_narration_only(text)


@pytest.mark.parametrize("text", [
    "Wrote 5 reconciled rules to agg_chunk_0.json.",
    "Done — 4 targets merged, 1 flagged for review.",
    "No targets in my slice, wrote [].",
    "The colours are: red, green, blue.",            # ends mid-list but is an answer
])
def test_substantive_answers_are_left_alone(text):
    assert not looks_like_narration_only(text)


def test_a_long_message_is_never_treated_as_a_lead_in():
    body = "Let me explain the reconciliation: " + ("detail " * 100) + ":"
    assert not looks_like_narration_only(body)


def test_blank_content_with_real_reasoning_is_not_nudged():
    """A reasoning model that concluded in its side channel already has an answer —
    the executor salvages `reasoning` as the result."""
    assert not looks_like_narration_only("", "I checked the slice and it was empty.")


@pytest.mark.asyncio
async def test_narration_turn_is_nudged_then_the_agent_finishes():
    from yggdrasil_lm.testing import unparsed_tool_call  # noqa: F401  (kept import parity)
    backend = StubBackend([
        end_turn("\n\nNow let me resolve all the input field contexts:\n\n"),
        end_turn("Wrote 5 reconciled rules to agg_chunk_0.json."),
    ])
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Shard")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="reconcile")

    assert ctx.outputs[sub.node_id]["text"].startswith("Wrote 5")
    assert len(backend.calls) == TWO_BACKEND_CALLS
    assert any("did not finish the task" in str(m.get("content", ""))
               for m in backend.calls[1][2])


@pytest.mark.asyncio
async def test_persistent_narration_terminates_bounded():
    backend = StubBackend(lambda *a: end_turn("\n\nLet me continue:"))
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Shard")
    sub = await app.add_subgraph("S", entry=agent)

    await app.run_subgraph(sub, query="reconcile")

    # initial turn + 2 bounded nudges, then accept — not max_iterations.
    assert len(backend.calls) == THREE_BACKEND_CALLS


# ── "done" means the artefacts exist (S3) ────────────────────────────────────
# An agent whose work is DEFINED by files it must leave behind has not finished while
# they are absent, however confident its closing message sounds. Declared generically
# as node.attributes["completion_paths"]; the engine only checks existence.

from yggdrasil_lm.core.executor import missing_completion_paths


def test_missing_paths_are_reported(tmp_path):
    present = tmp_path / "there.json"
    present.write_text("[]")
    absent = tmp_path / "missing.json"

    node = SimpleNamespace(attributes={"completion_paths": [str(present), str(absent)]})

    assert missing_completion_paths(node) == [str(absent)]


def test_all_present_means_nothing_missing(tmp_path):
    f = tmp_path / "a.json"
    f.write_text("[]")

    node = SimpleNamespace(attributes={"completion_paths": [str(f)]})

    assert missing_completion_paths(node) == []


def test_a_single_path_may_be_given_as_a_string(tmp_path):
    node = SimpleNamespace(attributes={"completion_paths": str(tmp_path / "nope.json")})

    assert missing_completion_paths(node) == [str(tmp_path / "nope.json")]


@pytest.mark.parametrize("attrs", [{}, {"completion_paths": []},
                                   {"completion_paths": None},
                                   {"completion_paths": 42}])
def test_nodes_without_a_declaration_are_unaffected(attrs):
    class N:
        attributes = attrs

    assert missing_completion_paths(N()) == []


def test_a_node_with_no_attributes_at_all_is_safe():
    class N:
        pass

    assert missing_completion_paths(N()) == []


@pytest.mark.asyncio
async def test_agent_is_told_to_write_its_missing_output_then_finishes(tmp_path):
    """The regression: the model says it is done while its output file is absent."""
    out = tmp_path / "shard_0.json"

    def _respond(*_a):
        # Second turn: actually create the artefact, then claim completion again.
        if len(backend.calls) >= TWO_BACKEND_CALLS:
            out.write_text("[]")
        return end_turn("Wrote the shard output.")

    backend = StubBackend(_respond)
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Shard")
    agent.attributes = {"completion_paths": [str(out)]}
    await app.store.upsert_node(agent)
    sub = await app.add_subgraph("S", entry=agent)

    await app.run_subgraph(sub, query="reconcile")

    assert out.exists()
    assert len(backend.calls) == TWO_BACKEND_CALLS
    assert any("do not exist yet" in str(m.get("content", ""))
               for m in backend.calls[1][2])


@pytest.mark.asyncio
async def test_persistently_absent_output_terminates_bounded(tmp_path):
    backend = StubBackend(lambda *a: end_turn("All done!"))
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Shard")
    agent.attributes = {"completion_paths": [str(tmp_path / "never.json")]}
    await app.store.upsert_node(agent)
    sub = await app.add_subgraph("S", entry=agent)

    await app.run_subgraph(sub, query="go")

    # initial turn + 2 bounded nudges, then accept — never max_iterations.
    assert len(backend.calls) == THREE_BACKEND_CALLS
