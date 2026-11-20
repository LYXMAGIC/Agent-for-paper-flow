# VSZ Patterns

Use these snippets as starting points when creating or modifying Veusz `.vsz` scripts. Match the existing file's style when editing. All new plots use the **青海蓝 + 橙色** palette (see SKILL.md § Color Theme).

## Color Palette

```python
# Primary series: 青海蓝
PlotLine__color='#87c1ca'   # light Qinghai-blue line
MarkerFill__color='#186582'  # dark Qinghai-blue marker

# Secondary series: grey-blue
PlotLine__color='#5d6673'    # grey-blue line (60% transparency)
MarkerFill__color='#5d6673'

# Accent / baseline / reference: orange
PlotLine__color='#ee982b'    # orange dotted/dashed
```

## Minimal XY Plot

```python
SetData('x', [0, 1, 2, 3])
SetData('y', [0, 1, 4, 9])

To(Add('page'))
To(Add('graph'))
Add('xy', xData='x', yData='y',
    PlotLine__color='#87c1ca', PlotLine__width='2pt',
    MarkerFill__color='#186582', marker='circle', markerSize='4pt')
Set('x/label', 'x')
Set('y/label', 'y')
```

If the graph is created with `autoadd=False`, add axes manually:

```python
To(Add('page'))
To(Add('graph', autoadd=False))
Add('axis', name='x')
Add('axis', name='y', direction='vertical')
Add('xy', xData='x', yData='y',
    PlotLine__color='#87c1ca', PlotLine__width='2pt',
    MarkerFill__color='#186582', marker='circle', markerSize='4pt')
```

## Function Overlay

```python
To('/page1/graph1')
Add('function', name='fit')
To('fit')
Set('function', 'a*x + b')
Set('Line/color', '#ee982b')       # orange accent
Set('Line/width', '1.5pt')
Set('Line/style', 'dashed')
To('..')
```

Use `SetDataExpression` if the function should be tied to datasets rather than rendered as a Veusz function widget.

## Axis Labels and Ranges

```python
Set('/page1/graph1/x/label', 'Time (s)')
Set('/page1/graph1/y/label', 'Signal (a.u.)')
Set('/page1/graph1/x/min', 0.0)
Set('/page1/graph1/x/max', 10.0)
Set('/page1/graph1/y/min', 'Auto')
Set('/page1/graph1/y/max', 'Auto')
```

Use absolute paths for robust edits in unfamiliar files. Use relative paths only when the current `To(...)` context is obvious.

## Styling an XY Dataset

Default theme colors:

```python
# Primary series
Set('/page1/graph1/xy1/PlotLine/color', '#87c1ca')
Set('/page1/graph1/xy1/PlotLine/width', '2pt')
Set('/page1/graph1/xy1/MarkerFill/color', '#186582')
Set('/page1/graph1/xy1/marker', 'circle')

# Secondary series
Set('/page1/graph1/xy2/PlotLine/color', '#5d6673')
Set('/page1/graph1/xy2/MarkerFill/color', '#5d6673')
```

When creating a widget, subsettings can also be set with double underscores:

```python
Add('xy', name='points', xData='x', yData='y',
    PlotLine__color='#87c1ca', MarkerFill__color='#186582')
```

## CSV Import

```python
ImportFileCSV('data.csv', delimiter=',', headermode='multi',
              linked=True, prefix='run1_')
Add('xy', xData='run1_time', yData='run1_signal',
    PlotLine__color='#87c1ca', PlotLine__width='2pt',
    MarkerFill__color='#186582', marker='circle', markerSize='4pt')
```

Prefer `linked=True` when the `.vsz` should refresh from the source data file. Prefer `SetData(...)` when the document should be self-contained.

## Multi-Panel Page

```python
To(Add('page'))
To(Add('grid', columns=2, rows=1))

To(Add('graph'))
Add('xy', xData='x1', yData='y1',
    PlotLine__color='#87c1ca', PlotLine__width='2pt',
    MarkerFill__color='#186582', marker='circle', markerSize='4pt')
To('..')

To(Add('graph'))
Add('xy', xData='x2', yData='y2',
    PlotLine__color='#87c1ca', PlotLine__width='2pt',
    MarkerFill__color='#186582', marker='circle', markerSize='4pt')
To('..')
```

Existing files may use explicit widget names. Preserve those names if other paths depend on them.

## Baseline / Reference Line

```python
# Horizontal baseline spanning axis range
SetData('baseline_x', [xmin, xmax])
SetData('baseline_y', [yval, yval])

Add('xy', name='baseline', xData='baseline_x', yData='baseline_y',
    marker='none', PlotLine__color='#ee982b', PlotLine__width='1.5pt',
    PlotLine__style='dotted', key='baseline')
```

## Export Commands

Only export when the user explicitly requests it. When needed:

```python
Export('figure.pdf', page=0)
Export('figure.svg', page=0, svgtextastext=True)
Export('figure.png', page=0, dpi=300)
```

Avoid committing export commands into a source `.vsz`. For rendering, use `scripts/render_vsz.py`.

## Editing Checklist

- Use the 青海蓝 + 橙色 palette for all new plots.
- Keep source data policy clear: linked import for refreshable external files, `SetData` for embedded data.
- Prefer absolute widget paths when changing existing projects.
- Check page numbers for `Export`; Veusz uses zero-based page indexes.
- Preserve user comments, names, and ordering when making targeted changes.
- Treat `.vsz` as executable Python and inspect before running unfamiliar files.
