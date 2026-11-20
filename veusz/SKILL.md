---
name: veusz
description: "Use when Codex needs to create, inspect, edit, import data into, or export Veusz scientific plotting projects (.vsz files and PDF/SVG/PNG outputs) using official Veusz script/API workflows, including direct .vsz editing, veusz --listen rendering, and Python integration through veusz.embed."
---

# Veusz

Use official Veusz control surfaces only: edit `.vsz` script files directly, execute/export with `veusz --listen`, or integrate Python through `veusz.embed`. Resolve the executable from `--veusz`, `VEUSZ_EXE`, or `veusz` on `PATH`; do not assume any installation directory. Do not introduce MCP servers, custom daemons, or non-official control layers.

## Color Theme

All new plots use the **青海蓝 (Qinghai-blue)** theme with **橙色 (orange)** accents:

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary (line) | 青海蓝 light | `#87c1ca` | Main data-series plot line |
| Primary (marker fill) | 青海蓝 dark | `#186582` | Main data-series marker fill |
| Secondary | Grey-blue | `#5d6673` | Secondary data-series line + marker |
| Accent | Orange | `#ee982b` | Baseline, reference lines, annotations |
| Highlight | 青海蓝 light | `#87c1ca` | Dashed highlight / guide lines |

When creating new plots, derive colors from this palette. For multi-series plots, cycle through lighter/darker shades of 青海蓝 before introducing other hues.

## Default Template

`assets/default-template.vsz` is the canonical multi-panel template: grid-based layout, 青海蓝 theme, orange baseline. It contains only synthetic demonstration data, not measurements. Use it as the starting point for new plots; replace datasets while preserving structure and styling. Do not interpret its example curves as experimental evidence. Read the template as text to see the full layout before creating new `.vsz` files.

## Workflow

**Always read the latest file first.** The user may have edited the `.vsz` file manually between sessions. Never rely on cached or prior-turn content — read the file as text or use `summarize_vsz.py` to inspect the current state before any modification.

1. Inspect the request and classify the task:
   - For reading or auditing an existing project, run `scripts/summarize_vsz.py` and inspect the `.vsz` text.
   - For simple plot changes, edit the `.vsz` script directly with Veusz commands.
   - For rendering/export, use `scripts/render_vsz.py` or send commands to `veusz --listen`.
   - For live Python-driven plotting, use official `veusz.embed`.
2. Before executing a user-supplied `.vsz`, inspect it for file operations, imports, plugin use, `Save`, `Export`, `Print`, and unexpected Python code. `.vsz` files are Python scripts interpreted by Veusz.
3. Prefer not to overwrite the source `.vsz`. Write modified copies or requested export files.
4. Do not use `--unsafe-mode` unless the user explicitly approves it for a trusted project.

## Local Tools

The helper scripts resolve the Veusz executable in this order: explicit `--veusz`, `VEUSZ_EXE`, then `veusz` on `PATH`. Python 3.10+ is required for the helpers. Use a Python environment selected for the current project, with Veusz installed separately or in that environment.

Run from this skill's directory (otherwise resolve helper paths relative to this `SKILL.md`):

```sh
python scripts/check_veusz.py
python scripts/summarize_vsz.py input.vsz
python scripts/render_vsz.py input.vsz output.pdf --page 0
```

If Veusz is outside `PATH`, pass `--veusz` with its location or configure `VEUSZ_EXE` locally. Do not commit machine-specific environment settings.

Use `check_veusz.py` when setup is uncertain. Use `summarize_vsz.py` before editing large or unfamiliar `.vsz` files. Use `render_vsz.py` for PDF/SVG/PNG export from a script file.

## Editing VSZ Files

`.vsz` documents are Veusz/Python command scripts. Keep edits idiomatic and close to existing style:

```python
SetData('x', [0, 1, 2, 3])
SetData('y', [0, 1, 4, 9])
To(Add('page'))
To(Add('graph'))
Add('xy', xData='x', yData='y',
    PlotLine__color='#87c1ca', PlotLine__width='2pt',
    MarkerFill__color='#186582', marker='circle', markerSize='4pt')
Set('x/label', 'Time (s)')
Set('y/label', 'Signal')
```

Read `references/veusz-api.md` for command signatures and semantics. Read `references/vsz-patterns.md` for common `.vsz` templates and modification patterns.

## Exporting

Only export when the user explicitly requests it. Do not auto-export PDF/SVG after every edit.

When exporting is requested, render with `veusz --listen` through `scripts/render_vsz.py`. The script sends `Load(...)`, `Export(...)`, and `Quit()` commands to Veusz over standard input.

Supported common export targets include `.pdf`, `.svg`, and `.png`; Veusz also supports other extensions through `Export`. Set the output extension to select the format.



### Known limitation: --listen vs GUI rendering

`veusz --listen` uses a headless rendering backend whose font metrics may differ slightly from the interactive GUI. This can cause:
- Key (legend) entry spacing to differ between GUI and export
- Widgets with manual positioning (`horzPosn='manual'` / `vertPosn='manual'`) to shift

**Mitigations (apply in `.vsz`):**
- Set explicit `Text/font` on key widgets (e.g. `'Times New Roman'`) — reduces font fallback variance
- When layout allows, prefer automatic anchor positioning (`'right'` / `'bottom'`) over manual coordinates
- For manual-positioned widgets near each other, add extra spacing as buffer (e.g. 0.02–0.05 in page-fractional units)
- **For publication-quality output where exact positioning matters: export from the Veusz GUI (`File → Export`)**, which uses the same rendering pipeline as the interactive view

## Python Embedding

Use `veusz.embed` only when Python code must construct or update a document programmatically. Prefer the new object API for new Python code and the path API when translating saved `.vsz` commands.

Read `references/embedding.md` before writing embedded Python or using `veusz --listen` directly.

## Security

Veusz checks scripts and expressions for security-sensitive operations. `Print()`, `Save()`, and `Export()` can trigger warnings in interactive contexts, and `--unsafe-mode` bypasses those checks. Keep `--unsafe-mode` off by default and treat unknown `.vsz` files as executable code.

## Shared Template Data

Keep packaged templates self-contained and synthetic. Do not copy user datasets, private project names, local import paths, linked files, or saved-session metadata into this skill. Removing an import path does not remove data already embedded in a `.vsz`; replace those arrays and their labels as well. Keep user inputs and generated exports outside the skill folder when preparing it for sharing.
