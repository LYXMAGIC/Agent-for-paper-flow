#!/usr/bin/env python
"""Statically summarize common Veusz commands in a .vsz file."""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from pathlib import Path
import re
import sys
from typing import Any


COMMANDS = {
    "Add",
    "Set",
    "SetData",
    "SetDataExpression",
    "SetDataRange",
    "SetData2D",
    "SetData2DExpression",
    "SetData2DExpressionXYZ",
    "SetData2DXYFunc",
    "SetDataDateTime",
    "SetDataText",
    "ImportFile",
    "ImportFile2D",
    "ImportFileCSV",
    "ImportFileFITS",
    "ImportFileHDF5",
    "ImportFileND",
    "Export",
    "Save",
    "Load",
    "To",
    "AddCustom",
    "SetToReference",
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", sys.getdefaultencoding()):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def literal(node: ast.AST | None) -> Any:
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except Exception:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Call):
            return f"{call_name(node.func) or 'call'}(...)"
        return ast.unparse(node) if hasattr(ast, "unparse") else None


def keyword_value(call: ast.Call, name: str) -> Any:
    for keyword in call.keywords:
        if keyword.arg == name:
            return literal(keyword.value)
    return None


def collect_calls(tree: ast.AST) -> list[tuple[int, str, ast.Call]]:
    calls: list[tuple[int, str, ast.Call]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node.func)
            if name in COMMANDS:
                calls.append((getattr(node, "lineno", 0), name, node))
    calls.sort(key=lambda item: item[0])
    return calls


def regex_calls(text: str) -> list[tuple[int, str, str]]:
    pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)$")
    out: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = pattern.match(line)
        if match and match.group(1) in COMMANDS:
            out.append((lineno, match.group(1), line.strip()))
    return out


def format_value(value: Any) -> str:
    if value is None:
        return "?"
    return repr(value)


def summarize_ast(path: Path, text: str) -> str:
    tree = ast.parse(text, filename=str(path))
    calls = collect_calls(tree)
    counts = Counter(name for _, name, _ in calls)
    datasets: dict[str, list[int]] = defaultdict(list)
    imports: list[str] = []
    exports: list[str] = []
    saves: list[str] = []
    widgets: list[str] = []
    navigation: list[str] = []
    settings: list[str] = []

    for lineno, name, call in calls:
        first = literal(call.args[0]) if call.args else None
        if name.startswith("SetData"):
            datasets[str(first)].append(lineno)
        elif name.startswith("ImportFile"):
            imports.append(f"line {lineno}: {name} {format_value(first)}")
        elif name == "Export":
            exports.append(f"line {lineno}: Export {format_value(first)}")
        elif name == "Save":
            saves.append(f"line {lineno}: Save {format_value(first)}")
        elif name == "Add":
            widget_type = first
            widget_name = keyword_value(call, "name")
            widgets.append(
                f"line {lineno}: Add type={format_value(widget_type)} name={format_value(widget_name)}"
            )
        elif name == "To":
            navigation.append(f"line {lineno}: To {format_value(first)}")
        elif name == "Set":
            settings.append(f"line {lineno}: Set {format_value(first)}")

    lines = [
        f"File: {path}",
        f"Lines: {len(text.splitlines())}",
        "",
        "Command counts:",
    ]
    if counts:
        lines.extend(f"  {name}: {count}" for name, count in counts.most_common())
    else:
        lines.append("  none")

    lines.extend(["", "Datasets:"])
    if datasets:
        for name, linenos in sorted(datasets.items()):
            joined = ", ".join(str(n) for n in linenos)
            lines.append(f"  {name}: lines {joined}")
    else:
        lines.append("  none found from SetData* calls")

    sections = [
        ("Imports", imports),
        ("Exports", exports),
        ("Saves", saves),
        ("Widget additions", widgets),
        ("Navigation", navigation),
        ("Setting changes", settings),
    ]
    for title, values in sections:
        lines.extend(["", f"{title}:"])
        if values:
            lines.extend(f"  {value}" for value in values[:80])
            if len(values) > 80:
                lines.append(f"  ... {len(values) - 80} more")
        else:
            lines.append("  none")

    return "\n".join(lines)


def summarize_regex(path: Path, text: str, error: SyntaxError) -> str:
    calls = regex_calls(text)
    counts = Counter(name for _, name, _ in calls)
    lines = [
        f"File: {path}",
        f"Lines: {len(text.splitlines())}",
        "",
        f"Python parse failed: {error}",
        "Using regex fallback.",
        "",
        "Command counts:",
    ]
    if counts:
        lines.extend(f"  {name}: {count}" for name, count in counts.most_common())
    else:
        lines.append("  none")
    lines.extend(["", "Command lines:"])
    if calls:
        lines.extend(f"  line {lineno}: {line}" for lineno, _, line in calls[:120])
        if len(calls) > 120:
            lines.append(f"  ... {len(calls) - 120} more")
    else:
        lines.append("  none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vsz", type=Path, help="Path to a Veusz .vsz file")
    args = parser.parse_args(argv)

    if not args.vsz.is_file():
        print(f"error: file not found: {args.vsz}", file=sys.stderr)
        return 2

    text = read_text(args.vsz)
    try:
        output = summarize_ast(args.vsz, text)
    except SyntaxError as exc:
        output = summarize_regex(args.vsz, text, exc)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
