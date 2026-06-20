"""Hatchling build hook: compile .coco → .py before wheel/sdist build."""

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CoconutBuildHook(BuildHookInterface):
    PLUGIN_NAME = "coconut"

    def initialize(self, version: str, build_data: dict) -> None:
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "coconut", "yggdrasil_lm/", "--target", "sys", "--quiet"],
            capture_output=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"coconut compilation failed (exit {result.returncode})")
