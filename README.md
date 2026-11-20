# Agent for paper flow（figure part）

面向 AI 助手的科学绘图与图示编辑技能，包含 **Veusz** 和 **Fig2Drawio**，用于创建科学绘图项目，以及将截图重建为可编辑的技术图示。

本仓库提供技能说明、辅助脚本和演示模板，**不包含 Veusz 和 draw.io 软件本体**。

## 功能介绍

| 技能 | 主要用途 | 输出格式 |
| --- | --- | --- |
| `veusz` | 创建、检查和修改科学绘图项目，按需导出图形 | `.vsz`、PDF、SVG、PNG 等 |
| `fig2drawio` | 根据参考图片重建文字、形状、布局和连接线 | `.drawio` |

### Veusz

- 使用官方 Veusz 脚本与 API 工作流。
- 支持数据集、坐标轴、曲线、图例及多面板布局。
- 提供环境检查、项目静态摘要和图形导出脚本。
- 内置青海蓝与橙色配色的双面板模板。
- 模板全部使用合成演示数据，不包含真实实验数据。

### Fig2Drawio

- 根据参考图片识别文字、布局、配色、形状及箭头。
- 使用固定坐标的 draw.io XML 重建可编辑图示。
- 提供压缩文件生成与往返校验脚本。
- 适用于流程图、架构图、框图和技术示意图。

## 安装与依赖

### 1. 下载并安装配套软件

使用前，请安装所需技能对应的软件；完整使用两个技能时，请安装两款软件。

| 软件 | 用途 | 官方下载链接 |
| --- | --- | --- |
| **Veusz** | 打开、编辑和渲染 `.vsz` 科学绘图项目，导出 PDF、SVG、PNG 等格式 | [下载 Veusz](https://veusz.github.io/download/) |
| **draw.io Desktop** | 打开、检查和编辑生成的 `.drawio` 图示 | [下载 draw.io 桌面版](https://github.com/jgraph/drawio-desktop/releases/latest) |

请根据自己的操作系统，在下载页面选择对应的安装包。

Fig2Drawio 的文件生成脚本可以独立运行；生成后，使用 draw.io Desktop 打开文件，检查布局并继续编辑。

### 2. 安装技能

下载或克隆本仓库，将需要的技能文件夹放入所使用 AI 工具支持的技能目录，并保留内部文件结构：

```text
技能目录/
├── veusz/
│   ├── SKILL.md
│   └── ...
└── fig2drawio/
    ├── SKILL.md
    └── ...
```

具体安装位置及加载方式，以对应 AI 工具的配置为准。

### 3. 准备 Python 环境

辅助脚本需要 **Python 3.10 或更新版本**，使用 Python 标准库。

Veusz 辅助脚本依次通过以下方式查找可执行程序：

1. 命令行参数 `--veusz`
2. 环境变量 `VEUSZ_EXE`
3. 系统 `PATH` 中的 `veusz`

如果安装后无法自动找到 Veusz，可通过 `--veusz` 指定其可执行程序的位置。

使用 Python 嵌入接口时，还需确保当前 Python 环境可以导入 `veusz.embed`。

## 使用方式

### 通过 AI 助手调用

在支持技能调用的 AI 工具中，可以参考以下请求：

**创建科学绘图：**

```text
使用 $veusz，根据提供的数据创建双面板折线图，
保留可编辑的 .vsz 项目，并导出 SVG。
```

**修改已有绘图：**

```text
使用 $veusz，检查这个 .vsz 文件，
调整坐标轴标签、曲线配色和图例位置，另存为新项目。
```

**重建图片中的图示：**

```text
使用 $fig2drawio，将这张架构截图重建为可编辑的 .drawio 文件，
尽量保留原图的文字、配色、布局和箭头样式。
```

请同时提供相应的数据、项目文件或参考图片。

### 直接运行辅助脚本

以下命令均在仓库根目录运行。

**检查 Veusz 环境：**

```sh
python veusz/scripts/check_veusz.py
```

**静态检查绘图项目：**

```sh
python veusz/scripts/summarize_vsz.py input.vsz
```

**将绘图项目导出为 SVG：**

```sh
python veusz/scripts/render_vsz.py input.vsz output.svg --page 0
```

**将绘图项目导出为 PNG：**

```sh
python veusz/scripts/render_vsz.py input.vsz output.png --page 0 --dpi 300
```

`--page` 使用从 `0` 开始的页面索引。已有输出文件默认不会被覆盖；需要替换时，可添加 `--overwrite`。

**生成 draw.io 文件：**

```sh
python fig2drawio/scripts/make_drawio.py --input model.xml --output figure.drawio
```

先由 AI 助手或其他工具生成 `mxGraphModel` XML，再运行上述命令。该脚本负责文件封装、压缩和校验；图片内容识别与布局重建由 AI 助手完成。

## 仓库结构

```text
.
├── veusz/
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   ├── assets/
│   │   └── default-template.vsz
│   ├── references/
│   │   ├── embedding.md
│   │   ├── veusz-api.md
│   │   └── vsz-patterns.md
│   └── scripts/
│       ├── check_veusz.py
│       ├── summarize_vsz.py
│       └── render_vsz.py
├── fig2drawio/
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   └── drawio-replica-notes.md
│   └── scripts/
│       └── make_drawio.py
├── 无害化说明.md
└── README.md
```

## 模板与数据安全

本仓库的分享版本已移除原有的本机固定路径、私人项目标识和模板实验数据。具体修改及验证范围见 `无害化说明.md`。

使用时请注意：

- 默认 Veusz 模板仅包含合成演示数据，不代表实验结果。
- 用户输入、实际数据和生成结果应保存在独立工作目录中，避免混入技能发布文件。
- `.vsz` 是可执行脚本，运行陌生文件前应检查其内容。
- draw.io 的压缩与 Base64 编码不会隐藏敏感信息。分享图稿前，应检查文字、隐藏单元格、额外页面、自定义属性和资源链接。
- 本地图稿优先使用本地应用预览。使用在线编辑器或外部预览服务时，应确认相关内容适合上传。

## 使用边界

图示重建的准确度受原图清晰度、文字可读性、字体和图形复杂度影响。生成后，请对照原图检查文字、连接关系和布局。

Veusz 的命令行导出与图形界面可能存在字体或间距差异。对排版精度要求较高时，请检查最终导出文件，必要时使用 Veusz 图形界面导出。

## 相关软件

- [Veusz 官方网站](https://veusz.github.io/)
- [Veusz 下载页面](https://veusz.github.io/download/)
- [draw.io 官方网站](https://www.drawio.com/)
- [draw.io Desktop 下载页面](https://github.com/jgraph/drawio-desktop/releases/latest)
