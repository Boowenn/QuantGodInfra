from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "qg-split-path-guard.py"
spec = importlib.util.spec_from_file_location("qg_split_path_guard", MODULE_PATH)
assert spec is not None and spec.loader is not None
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class SplitPathGuardTests(unittest.TestCase):
    def test_detects_old_monorepo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "automation.toml"
            path.write_text('cwds = ["/Users/bowen/Desktop/Quard/QuantGod"]\n', encoding="utf-8")
            issues = guard.find_issues([path])
            self.assertEqual(1, len(issues))

    def test_allows_split_repo_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "workspace.json"
            path.write_text(
                "/Users/bowen/Desktop/Quard/QuantGodBackend\n"
                "/Users/bowen/Desktop/Quard/QuantGodFrontend\n",
                encoding="utf-8",
            )
            self.assertEqual([], guard.find_issues([path]))


if __name__ == "__main__":
    unittest.main()
