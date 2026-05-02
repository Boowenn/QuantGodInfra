#!/usr/bin/env python3
"""Multi-repo workspace helper for QuantGod."""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
from typing import Sequence


def load_workspace(path: pathlib.Path) -> dict:
    if not path.exists():
        raise SystemExit(f"workspace file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ["backend", "frontend", "infra", "docs"]:
        if key not in data:
            raise SystemExit(f"workspace missing key: {key}")
    return data


def run(cmd: Sequence[str], cwd: pathlib.Path, check: bool = True) -> int:
    print(f"\n$ {' '.join(cmd)}\n  cwd={cwd}")
    proc = subprocess.run(list(cmd), cwd=str(cwd), text=True)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def repo_paths(ws: dict) -> dict[str, pathlib.Path]:
    return {key: pathlib.Path(ws[key]).resolve() for key in ["backend", "frontend", "infra", "docs"]}


def cmd_status(ws: dict) -> None:
    for name, path in repo_paths(ws).items():
        print(f"\n== {name}: {path}")
        run(["git", "status", "--short", "--branch"], path, check=False)


def cmd_pull(ws: dict) -> None:
    for path in repo_paths(ws).values():
        run(["git", "pull", "--ff-only"], path)


def cmd_test(ws: dict) -> None:
    paths = repo_paths(ws)
    run([sys.executable, "-m", "unittest", "discover", "tests", "-v"], paths["backend"])
    run(["node", "--test", "tests/node/*.mjs"], paths["backend"], check=False)
    run(["npm", "run", "build"], paths["frontend"])
    docs_check = paths["docs"] / "scripts" / "check_docs_links.py"
    if docs_check.exists():
        run([sys.executable, str(docs_check)], paths["docs"])


def cmd_build_frontend(ws: dict) -> None:
    paths = repo_paths(ws)
    pkg_lock = paths["frontend"] / "package-lock.json"
    run(["npm", "ci" if pkg_lock.exists() else "install"], paths["frontend"])
    run(["npm", "run", "build"], paths["frontend"])


def cmd_sync_frontend_dist(ws: dict) -> None:
    paths = repo_paths(ws)
    frontend_dist = paths["frontend"] / ws.get("frontendDist", "dist")
    backend_dist = paths["backend"] / ws.get("backendVueDist", "Dashboard/vue-dist")
    if not frontend_dist.exists():
        raise SystemExit(f"frontend dist missing; run build-frontend first: {frontend_dist}")
    if backend_dist.exists():
        shutil.rmtree(backend_dist)
    shutil.copytree(frontend_dist, backend_dist)
    print(f"synced {frontend_dist} -> {backend_dist}")


def cmd_verify(ws: dict) -> None:
    paths = repo_paths(ws)
    checks = [
        (paths["backend"] / "tools", True, "backend tools present"),
        (paths["backend"] / "MQL5", True, "backend MQL5 present"),
        (paths["backend"] / "frontend", False, "backend frontend removed"),
        (paths["frontend"] / "src", True, "frontend src present"),
        (paths["frontend"] / "tools", False, "frontend has no backend tools"),
        (paths["infra"] / "scripts" / "qg-workspace.py", True, "infra workspace helper present"),
        (paths["docs"] / "docs" / "architecture" / "repo-split.md", True, "docs split guide present"),
    ]
    failed = False
    for path, should_exist, label in checks:
        ok = path.exists() == should_exist
        print(f"{'OK' if ok else 'FAIL'}: {label} :: {path}")
        failed = failed or not ok
    if failed:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["status", "pull", "test", "build-frontend", "sync-frontend-dist", "verify"])
    parser.add_argument("--workspace", default="workspace/quantgod.workspace.json")
    args = parser.parse_args()
    ws = load_workspace(pathlib.Path(args.workspace).resolve())
    {
        "status": cmd_status,
        "pull": cmd_pull,
        "test": cmd_test,
        "build-frontend": cmd_build_frontend,
        "sync-frontend-dist": cmd_sync_frontend_dist,
        "verify": cmd_verify,
    }[args.command](ws)


if __name__ == "__main__":
    main()
