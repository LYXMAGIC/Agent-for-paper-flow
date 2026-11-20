#!/usr/bin/env python
"""Check local Veusz executable and Python embedding availability."""

from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys




def candidate_paths(explicit: str | None = None) -> list[tuple[str, Path | None]]:
    candidates: list[tuple[str, Path | None]] = []
    if explicit:
        candidates.append(("--veusz", Path(explicit).expanduser().resolve()))
    env_value = os.environ.get("VEUSZ_EXE")
    if env_value:
        candidates.append(("VEUSZ_EXE", Path(env_value).expanduser().resolve()))
    path_value = shutil.which("veusz")
    if path_value:
        candidates.append(("PATH", Path(path_value)))
    return candidates


def find_veusz(explicit: str | None = None) -> Path | None:
    for _, path in candidate_paths(explicit):
        if path and path.is_file():
            return path
    return None


def run_version(exe: Path) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [str(exe), "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=15,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return False, f"{type(exc).__name__}: {exc}"
    output = proc.stdout.strip()
    if not output:
        output = f"exit code {proc.returncode}"
    return proc.returncode == 0, output


def check_embed_import() -> tuple[bool, str]:
    try:
        spec = importlib.util.find_spec("veusz.embed")
    except ModuleNotFoundError:
        spec = None
    if spec is None:
        return False, "veusz.embed is not importable in this Python environment"
    try:
        import veusz.embed as veusz_embed  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return False, f"{type(exc).__name__}: {exc}"
    location = getattr(veusz_embed, "__file__", None) or "unknown location"
    return True, str(location)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--veusz", help="Explicit path to the Veusz executable")
    args = parser.parse_args(argv)

    print("Veusz executable candidates:")
    found = None
    for source, path in candidate_paths(args.veusz):
        status = "found" if path and path.is_file() else "missing"
        print(f"  {source}: {path} [{status}]")
        if found is None and path and path.is_file():
            found = path

    if found:
        ok, version = run_version(found)
        print(f"\nSelected executable: {found}")
        print(f"Version check: {'ok' if ok else 'failed'} - {version}")
    else:
        print("\nSelected executable: none")

    embed_ok, embed_msg = check_embed_import()
    print(f"\nPython: {sys.executable}")
    print(f"veusz.embed import: {'ok' if embed_ok else 'missing'} - {embed_msg}")

    return 0 if found or embed_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
