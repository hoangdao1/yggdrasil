"""Public API surface tests.

These tests assert that each module's __all__ contains exactly what it should
— no more, no less. They catch accidental promotion of internal helpers or
display functions into the wrong layer's public surface.

Layer model:
    yggdrasil.observability  — data API (explain_run, export_trace, cleanup helpers)
    yggdrasil.trace_ui       — terminal display (inspect_trace, print_trace)
    yggdrasil.viz            — browser UI (serve_trace, live_trace, VizServer)
"""

from __future__ import annotations

import yggdrasil_lm.observability as obs
import yggdrasil_lm.trace_ui as tui
import yggdrasil_lm.viz as viz


# ---------------------------------------------------------------------------
# observability — data API only
# ---------------------------------------------------------------------------

_OBS_INTERNAL_SYMBOLS = {"TraceView", "extract_trace_view"}


def test_observability_all_excludes_internal_helpers():
    """TraceView and extract_trace_view are internal helpers; must not be in observability.__all__."""
    for name in _OBS_INTERNAL_SYMBOLS:
        assert name not in obs.__all__, (
            f"{name!r} is an internal helper; remove it from observability.__all__ "
            f"or promote it to a documented public API with tests"
        )


def test_observability_all_contains_data_api():
    """Core data-API functions must be publicly exported."""
    required = {"explain_run", "export_trace", "RunExplanation"}
    for name in required:
        assert name in obs.__all__, f"{name!r} must be in yggdrasil.observability.__all__"


# ---------------------------------------------------------------------------
# trace_ui — terminal display only
# ---------------------------------------------------------------------------

def test_trace_ui_all_contains_display_functions():
    """Both display functions must be exported from the canonical terminal module."""
    assert "inspect_trace" in tui.__all__, "'inspect_trace' must be in yggdrasil.trace_ui.__all__"
    assert "print_trace" in tui.__all__, "'print_trace' must be in yggdrasil.trace_ui.__all__"


# ---------------------------------------------------------------------------
# viz — browser UI
# ---------------------------------------------------------------------------

def test_viz_all_contains_browser_functions():
    """Browser-layer entry points must be publicly exported."""
    required = {"serve_trace", "live_trace", "VizServer"}
    for name in required:
        assert name in viz.__all__, f"{name!r} must be in yggdrasil.viz.__all__"


# ---------------------------------------------------------------------------
# Canonical import paths work
# ---------------------------------------------------------------------------

def test_canonical_import_trace_ui():
    from yggdrasil_lm.trace_ui import inspect_trace, print_trace
    assert callable(inspect_trace)
    assert callable(print_trace)


def test_canonical_import_observability():
    from yggdrasil_lm.observability import explain_run
    assert callable(explain_run)


def test_canonical_import_viz():
    from yggdrasil_lm.viz import serve_trace, live_trace
    assert callable(serve_trace)
    assert callable(live_trace)


def test_top_level_namespace_re_exports_all_layers():
    """yggdrasil top-level re-exports functions from all three layers for convenience."""
    import yggdrasil_lm
    assert hasattr(yggdrasil, "inspect_trace")
    assert hasattr(yggdrasil, "print_trace")
    assert hasattr(yggdrasil, "explain_run")
