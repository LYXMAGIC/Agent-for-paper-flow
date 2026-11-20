# Veusz API Notes

These notes summarize the official Veusz command/API surface most often needed by Codex when editing `.vsz` scripts or driving `veusz --listen`.

## Command Contexts

Veusz uses one command API across the GUI console, embedded Python, plugins, saved `.vsz` documents, and external control with `veusz --listen`. Saved `.vsz` files are Python scripts containing Veusz commands.

The GUI console allows a simplified syntax, but `.vsz` files and automation should use regular Python call syntax.

## Navigation and Widgets

```python
To('widgetpath')
```

Move the current position in the widget tree. Paths are Unix-like: `/` is root, `..` is parent, and examples include `graph1`, `/page1/graph1/x`, and `../x`.

```python
Add('widgettype', name='nameforwidget', autoadd=True, optionalargs)
```

Add a widget under the current widget and return its name. Common widget types include `page`, `graph`, `axis`, `xy`, `function`, `grid`, `label`, `key`, and 2D/3D plot widgets. `autoadd=True` creates default children such as graph axes. Subsettings can be initialized with double underscores:

```python
Add('axis', name='y', direction='vertical')
Add('xy', MarkerFill__color='red', ErrorBarLine__hide=True)
```

## Settings

```python
Set('settingpath', val)
Get('settingpath')
GetChildren(where='.')
```

`Set` changes a setting by path. The path can be absolute or relative to the current widget. Setting groups use `/`, for example `MarkerFill/color` or `PlotLine/width`.

Examples:

```python
Set('/page1/graph1/x/min', -10.0)
Set('x/label', 'Time (s)')
Set('y/direction', 'vertical')
Set('xy1/MarkerFill/color', 'cyan')
value = Get('/page1/graph1/x/min')
children = GetChildren('/page1/graph1')
```

## Data

```python
SetData(name, val, symerr=None, negerr=None, poserr=None)
SetDataExpression(name, expr, linked=False)
SetDataRange(name, numsteps, val, symerr=None, negerr=None, poserr=None, linked=False)
SetData2D('name', val, xrange=(A, B), yrange=(C, D), xgrid=None, ygrid=None)
SetDataText(name, val)
```

Use `SetData` for 1D numeric datasets. `val` and error arrays may be Python lists or NumPy arrays. `None` values are left blank. Use the expression/range variants when the dataset should be linked to an expression or generated range.

Examples:

```python
SetData('x', [0, 1, 2, 3])
SetData('y', [0, 1, 4, 9], symerr=[0.1, 0.2, 0.2, 0.3])
SetDataExpression('residual', 'y - model', linked=True)
SetDataText('labels', ['A', 'B', 'C'])
```

## Data Import

```python
ImportFileCSV('filename', readrows=False, delimiter=',', skipwhitespace=False,
              textdelimiter='"', encoding='utf_8', headerignore=0,
              rowsignore=0, blanksaredata=False, numericlocale='en_US',
              dateformat='YYYY-MM-DD|T|hh:mm:ss', headermode='multi',
              dsprefix='', dssuffix='', prefix=None, renames=None,
              linked=False)
```

Use `ImportFileCSV` for CSV files. Dataset names normally come from headers. Use `prefix`, `dsprefix`, `dssuffix`, or `renames` to avoid collisions or map column names.

Other useful import commands include `ImportFile`, `ImportFile2D`, `ImportFileFITS`, `ImportFileHDF5`, `ImportFileND`, and plugin-based import commands for specialized formats.

## Load, Save, and Export

```python
Load('filename.vsz')
Save('filename.vsz')
Export(filename, color=True, page=0, dpi=100, antialias=True, quality=85,
       backcolor='#ffffff00', pdfdpi=150, svgdpi=96, svgtextastext=False)
```

`Load` loads a Veusz script file from the command line or `--listen` context. It is not for use inside a saved script. `Save` writes the current document. `Export` exports a page, where `page` is zero-based. The output type is selected by filename extension. Officially supported extensions include `.eps`, `.pdf`, `.ps`, `.svg`, `.jpg`, `.jpeg`, `.bmp`, and `.png`.

Examples:

```python
Export('figure.pdf', page=0)
Export('figure.svg', page=0, svgtextastext=True)
Export('figure.png', page=0, dpi=300, antialias=True)
```

## Listen-Only or Embedded-Only Commands

```python
Quit()
Zoom(factor)
ForceUpdate()
EnableToolbar(enable=True)
MoveToPage(pagenum)
ResizeWindow(width, height)
```

`Quit` is only supported by `veusz --listen`. `Zoom`, `ForceUpdate`, toolbar, page movement, and window resize commands are for embedded or `--listen` workflows.

## Safety

Veusz applies security checks to scripts and expressions. Operations such as file access, imports, `Save`, `Export`, and `Print` can trigger warnings in GUI contexts. Do not use `--unsafe-mode` unless the user explicitly approves it for trusted input.
