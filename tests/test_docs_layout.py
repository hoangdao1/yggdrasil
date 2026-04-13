from pathlib import Path


def test_beginner_docs_exist():
    root = Path(__file__).resolve().parents[1]
    expected = [
        root / "CONTRIBUTING.md",
        root / "docs" / "start-here.md",
        root / "docs" / "first-graph.md",
        root / "docs" / "choose-backend.md",
        root / "docs" / "architecture.md",
        root / "docs" / "repo-map.md",
        root / "docs" / "devex-roadmap.md",
        root / "docs" / "control-plane-thesis.md",
        root / "docs" / "explainable-systems.md",
        root / "docs" / "flagship-workflow.md",
    ]
    for path in expected:
        assert path.exists(), f"missing expected doc: {path}"
