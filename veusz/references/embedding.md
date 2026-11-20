# Veusz Embedding and Listen Mode

Use this reference when Python code must drive Veusz or when direct `veusz --listen` control is needed.

## Choosing an Interface

- Edit `.vsz` directly for reproducible static project changes.
- Use `veusz --listen` for batch execution/export from outside Python or from automation scripts.
- Use `veusz.embed` when Python must construct, update, or interact with a Veusz document live.
- Prefer the new object API for new embedded Python code.
- Prefer the older path API when translating saved `.vsz` commands.

## External Control with `veusz --listen`

`veusz --listen` reads Python/Veusz commands from standard input and writes output to standard output. It supports the normal scripting commands plus `Quit()`, `EnableToolbar()`, and `Zoom(...)`.

Example command stream:

```python
To(Add('page'))
To(Add('graph'))
SetData('x', arange(20))
SetData('y', arange(20)**2)
Add('xy')
Export('foo.pdf')
Quit()
```

Shell usage:

```sh
veusz --listen < in.vsz
```

This redirection example uses a POSIX shell. In PowerShell, use the Python renderer below. Configure the executable via `--veusz`, `VEUSZ_EXE`, or `PATH`.

In Codex workflows, prefer `scripts/render_vsz.py` because it handles executable discovery, output paths, timeouts, and the `Load(...)`/`Export(...)`/`Quit()` command sequence.

## Older Path-Based Embedded API

```python
import numpy
import veusz.embed as veusz

g = veusz.Embedded('window title')
g.EnableToolbar()
g.To(g.Add('page'))
g.To(g.Add('graph'))
g.Add('xy', marker='tiehorz', MarkerFill__color='green')
g.Set('x/autoExtend', False)
g.SetData('x', numpy.arange(0, 7, 0.05))
g.SetData('y', numpy.sin(g.GetData('x')[0]))
g.Export('figure.pdf')
g.Close()
```

The embedded object exposes most commands from the command-line API as methods.

## New Object API

The object API exposes the document tree through `Embedded.Root`. Widgets, setting groups, and settings are `Node` objects. Read or write setting values with `.val`.

```python
import veusz.embed

embed = veusz.embed.Embedded('window title')
page = embed.Root.Add('page')
graph = page.Add('graph')
func = graph.Add('function', function='x**2')
func.function.val = 'x**3'
graph.x.label.val = 'x'
graph.y.label.val = 'f(x)'
embed.Export('function.pdf')
embed.Close()
```

Use attribute access for simple names (`Root.page1.graph1`) and dictionary access when names contain spaces or collide with Node attributes (`Root['page 1']['graph 1']`).

Useful node properties and methods:

```python
node.path
node.type
node.name
node.children
node.childnames
node.parent
node.fromPath('/page1/graph1')
widget.WalkWidgets(widgettype='function')
widget.Add('xy', xData='x', yData='y')
widget.Rename('newname')
widget.Remove()
```

## Safety

Embedding and listen mode execute Python/Veusz commands. Do not run untrusted `.vsz` files or generated command streams without inspection. Keep `--unsafe-mode` disabled unless the user explicitly approves it for trusted content.
