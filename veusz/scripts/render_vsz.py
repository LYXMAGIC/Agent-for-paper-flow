#!/usr/bin/env python
"""Render a Veusz .vsz file through veusz --listen."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".svg",
    ".png",
    ".eps",
    ".ps",
    ".jpg",
    ".jpeg",
    ".bmp",
}
UTF8_BOM = b"\xef\xbb\xbf"


def resolve_veusz(explicit: str | None = None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser().resolve())
    env_value = os.environ.get("VEUSZ_EXE")
    if env_value:
        candidates.append(Path(env_value).expanduser().resolve())
    path_value = shutil.which("veusz")
    if path_value:
        candidates.append(Path(path_value))

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    searched = "\n".join(f"  {candidate}" for candidate in candidates)
    raise FileNotFoundError(f"Could not find Veusz. Set --veusz or VEUSZ_EXE, or add veusz to PATH. Searched:\n{searched}")


def build_command_stream(input_path: Path, output: Path, page: int, dpi: int | None) -> str:
    export_args = [repr(str(output)), f"page={page}"]
    if dpi is not None:
        export_args.append(f"dpi={dpi}")
    commands = [
        f"Load({repr(str(input_path))})",
        f"Export({', '.join(export_args)})",
        "Quit()",
    ]
    return "\n".join(commands) + "\n"


def prepare_load_path(input_path: Path) -> tuple[Path, Path | None]:
    """Return a Veusz-loadable path and an optional temp file to delete."""
    data = input_path.read_bytes()
    if not data.startswith(UTF8_BOM):
        return input_path, None

    text = data.decode("utf-8-sig")
    with tempfile.NamedTemporaryFile("w", suffix=".vsz", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        return Path(handle.name), Path(handle.name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input .vsz file")
    parser.add_argument("output", type=Path, help="Output file, for example .pdf/.svg/.png")
    parser.add_argument("--page", type=int, default=0, help="Zero-based page index to export")
    parser.add_argument("--dpi", type=int, help="Raster export DPI")
    parser.add_argument("--veusz", help="Path to the Veusz executable. Defaults to VEUSZ_EXE, then veusz on PATH.")
    parser.add_argument("--timeout", type=int, default=120, help="Render timeout in seconds")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing output file")
    parser.add_argument(
        "--unsafe-mode",
        action="store_true",
        help="Pass --unsafe-mode to Veusz. Use only for trusted scripts with explicit approval.",
    )
    args = parser.parse_args(argv)

    input_path = args.input.resolve()
    output_path = args.output.resolve()

    if not input_path.is_file():
        print(f"error: input file not found: {input_path}", file=sys.stderr)
        return 2
    if input_path.suffix.lower() != ".vsz":
        print(f"error: input file must have .vsz extension: {input_path}", file=sys.stderr)
        return 2
    if output_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(f"error: unsupported output extension {output_path.suffix!r}. Supported: {supported}", file=sys.stderr)
        return 2
    if output_path.exists() and not args.overwrite:
        print(f"error: output exists; pass --overwrite to replace it: {output_path}", file=sys.stderr)
        return 2
    if args.page < 0:
        print("error: --page must be >= 0", file=sys.stderr)
        return 2
    if args.dpi is not None and args.dpi <= 0:
        print("error: --dpi must be positive", file=sys.stderr)
        return 2

    try:
        veusz_exe = resolve_veusz(args.veusz)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        load_path, cleanup_path = prepare_load_path(input_path)
    except OSError as exc:
        print(f"error: failed to prepare input file: {exc}", file=sys.stderr)
        return 1

    command_stream = build_command_stream(load_path, output_path, args.page, args.dpi)
    cmd = [str(veusz_exe), "--listen"]
    if args.unsafe_mode:
        cmd.append("--unsafe-mode")

    try:
        proc = subprocess.run(
            cmd,
            input=command_stream,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(input_path.parent),
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"error: Veusz render timed out after {args.timeout}s", file=sys.stderr)
        return 1
    finally:
        if cleanup_path is not None:
            try:
                cleanup_path.unlink()
            except OSError:
                pass

    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)

    combined_output = f"{proc.stdout}\n{proc.stderr}"
    if "Traceback (most recent call last)" in combined_output or "SyntaxError:" in combined_output:
        print("error: Veusz reported a script traceback", file=sys.stderr)
        return 1
    if proc.returncode != 0:
        print(f"error: Veusz exited with code {proc.returncode}", file=sys.stderr)
        return proc.returncode or 1
    if not output_path.is_file() or output_path.stat().st_size <= 0:
        print(f"error: output was not created or is empty: {output_path}", file=sys.stderr)
        return 1

    print(f"Rendered {input_path} -> {output_path} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
