---
name: fig2drawio
description: Recreate a user-provided screenshot or image as an editable diagrams.net/draw.io diagram, especially when the user asks to replicate, restore, convert, or redraw a figure as a .drawio file with high visual fidelity.
---

# Fig2Drawio

## When To Use

Use this skill when the user provides a screenshot/image and asks for an editable draw.io/diagrams.net version, a `.drawio` file, or a high-fidelity redraw of a diagram. It is intended for static technical figures, workflows, architecture diagrams, paper figures, block diagrams, and annotated schematics.

## Workflow

1. Inspect the screenshot visually before generating anything. Identify canvas size, major regions, text, font hierarchy, colors, stroke widths, arrow styles, line routing, rounded corners, shadows, dashed boxes, legends, and repeated elements.
2. Choose draw.io XML for high-fidelity replication. Avoid Mermaid unless the user explicitly accepts approximate layout.
3. Build the diagram as an `mxGraphModel` with fixed coordinates. Use explicit colors, sizes, line styles, arrowheads, and `html=1` labels.
4. Preserve the source language and symbols exactly. For Chinese/English mixed labels, copy the text as shown, including punctuation, multiplication signs, percentages, arrows, and line breaks.
5. Save a local `.drawio` file first. Prefer a local diagrams.net desktop application for preview. Use an online editor or connected preview service only when the user requests that destination; availability alone does not authorize uploading screenshots, labels, XML, or embedded assets.
6. Always create a diagrams.net-compatible compressed `.drawio` file with `scripts/make_drawio.py`; do not rely only on a raw `mxfile` wrapper.
7. Validate the output by round-tripping the compressed payload with the script and, when practical, opening the file in diagrams.net.

## Output Rules

- Put the final `.drawio` file in the user's working directory unless they request another location.
- Prefer a descriptive filename based on the figure, such as `figure_replicated.drawio`.
- Tell the user the exact file path and whether it was opened successfully.
- If the user reports `Invalid file data`, regenerate using `scripts/make_drawio.py --input <xml> --output <file.drawio>`.

## Fidelity Checklist

Before finalizing, compare against the screenshot for:

- all visible text and line breaks
- section headers and numbered labels
- box positions, sizes, fills, borders, corner radius, and shadows
- solid, dashed, bidirectional, and colored arrows
- bracket/brace marks, ellipses, plus signs, legends, and callouts
- visual hierarchy and spacing between top, middle, and bottom regions

For detailed XML and compatibility notes, read `references/drawio-replica-notes.md` only when needed.

## Portable Local Usage

The helper uses Python 3.10+ and the standard library only; it makes no network requests. Resolve its path relative to this `SKILL.md`, rather than a fixed home directory. Run from this skill directory:

```sh
python scripts/make_drawio.py --input model.xml --output figure.drawio
```

## Shared Assets and Data

This skill ships no source screenshots, real project diagrams, or private datasets. Keep user inputs and generated diagrams in the user-selected working directory, outside the installed skill. For shareable examples, use synthetic labels and shapes. Inspect labels, custom properties, hyperlinks, image references, hidden cells, and extra pages before sharing a generated diagram: compression and base64 encoding do not anonymize its content. Prefer native shapes and embedded, authorized assets over local file references or remote image URLs.
