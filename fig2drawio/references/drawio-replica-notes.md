# Draw.io Replica Notes

## Visual Extraction

When replicating a screenshot, first make a concise inventory:

- Canvas aspect ratio and approximate pixel bounds.
- Top-level regions and their bounding boxes.
- Repeated components, such as headers, modules, engines, legends, and result boxes.
- Text exactly as rendered, preserving Chinese punctuation and mixed English terms.
- Color families: fill, stroke, font, arrows, dashed paths.
- Connector semantics: solid data flow, reuse arrows, dashed reuse paths, bidirectional arrows, and arrowhead type.

## XML Generation Guidelines

- Use `mxGraphModel` with explicit page size and `grid="0"` for screenshot-like placement.
- Use draw.io XML rather than Mermaid for high-fidelity fixed layout.
- Add `html=1` to styles when labels contain `<br>`, `<b>`, `<font>`, or escaped HTML.
- Escape XML attribute values: `&`, `<`, `>`, and quotes.
- Use unique `id` values for every `mxCell`.
- Every edge must contain `<mxGeometry relative="1" as="geometry"/>`.
- For arrows that must look exactly positioned, create small invisible point vertices and connect them instead of depending only on shape perimeter routing.
- For text-only bracket marks, use a `text` shape with a large font size.

## File Compatibility

diagrams.net accepts both uncompressed and compressed files in many cases, but some environments reject raw wrapped XML with `Invalid file data`. Prefer compressed diagram payloads:

1. Extract or create the inner `mxGraphModel`.
2. URL-encode the model XML.
3. Raw-deflate it with zlib using `wbits=-15`.
4. Base64 encode the compressed bytes.
5. Put that payload inside `<diagram>...</diagram>` in `<mxfile>`.

Use `scripts/make_drawio.py` to perform this deterministically.

## Troubleshooting

- `Invalid file data`: regenerate with the compressed writer script.
- Browser did not open: still provide the local `.drawio` path and optionally start the file with `Start-Process`.
- Text shows raw HTML tags: the cell style is missing `html=1` or label escaping is wrong.
- `<<` displays incorrectly: use `&amp;lt;&amp;lt;` in an XML attribute value.
- Lines route differently than the screenshot: use invisible anchor vertices for strict routes.
