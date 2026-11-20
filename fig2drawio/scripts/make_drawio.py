#!/usr/bin/env python3
"""Create diagrams.net-compatible .drawio files from mxGraphModel XML.

The script accepts either:
- an mxGraphModel XML file, or
- an mxfile containing one diagram with an mxGraphModel child.

By default it writes a compressed diagrams.net payload, which avoids
"Invalid file data" failures seen with some raw XML wrappers.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib


def read_model_xml(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    root = ET.fromstring(text)

    if root.tag == "mxGraphModel":
        model = root
    elif root.tag == "mxfile":
        diagram = root.find("diagram")
        if diagram is None:
            raise ValueError("mxfile has no diagram element")
        children = list(diagram)
        if not children:
            raise ValueError("diagram has no mxGraphModel child; compressed input is not supported")
        model = children[0]
        if model.tag != "mxGraphModel":
            raise ValueError(f"expected mxGraphModel child, got {model.tag!r}")
    else:
        raise ValueError(f"expected mxGraphModel or mxfile root, got {root.tag!r}")

    return ET.tostring(model, encoding="unicode", short_empty_elements=True)


def compress_model(model_xml: str) -> str:
    encoded = urllib.parse.quote(model_xml, safe="-_.!~*'()")
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(encoded.encode("utf-8")) + compressor.flush()
    return base64.b64encode(compressed).decode("ascii")


def verify_payload(payload: str) -> None:
    inflated = zlib.decompress(base64.b64decode(payload), wbits=-15).decode("utf-8")
    model_xml = urllib.parse.unquote(inflated)
    root = ET.fromstring(model_xml)
    if root.tag != "mxGraphModel":
        raise ValueError("round-trip verification did not produce mxGraphModel")


def build_mxfile(payload: str, name: str, diagram_id: str, version: str) -> str:
    root = ET.Element("mxfile", {
        "host": "app.diagrams.net", "agent": "Codex",
        "version": version, "type": "device",
    })
    diagram = ET.SubElement(root, "diagram", {"id": diagram_id, "name": name})
    diagram.text = payload
    return ET.tostring(root, encoding="unicode", short_empty_elements=True) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Write a compatible compressed .drawio file")
    parser.add_argument("--input", "-i", required=True, type=Path, help="mxGraphModel XML or raw mxfile")
    parser.add_argument("--output", "-o", required=True, type=Path, help="output .drawio path")
    parser.add_argument("--name", default="Diagram", help="diagram page name")
    parser.add_argument("--id", default="diagram-1", help="diagram id")
    parser.add_argument("--version", default="24.7.17", help="diagrams.net version metadata")
    args = parser.parse_args(argv)

    model_xml = read_model_xml(args.input)
    payload = compress_model(model_xml)
    verify_payload(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_mxfile(payload, args.name, args.id, args.version), encoding="utf-8")
    print(args.output)
    print(f"bytes={args.output.stat().st_size}")
    print("compressed roundtrip OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
