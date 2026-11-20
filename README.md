# Agent for paper flow

面向 AI 助手的科学绘图与图示编辑技能，包含 **Veusz** 和 **Fig2Drawio**：前者用于创建和修改科学绘图项目，后者用于将截图或图片重建为可编辑的 draw.io 图示。

## 功能

| 技能 | 用途 | 主要输出 |
| --- | --- | --- |
| `veusz` | 创建、检查和修改科学绘图项目，按需导出图形 | `.vsz`、PDF、SVG、PNG |
| `fig2drawio` | 根据参考图片重建布局、文字、形状和连接线 | `.drawio` |

### Veusz

- 使用官方 Veusz 脚本和 API 工作流。
- 支持数据集、坐标轴、曲线、图例和多面板布局。
- 提供静态项目摘要、环境检查和导出辅助脚本。
- 内置青海蓝与橙色配色的双面板模板，数据全部为合成示例。

### Fig2Drawio

- 根据参考图片识别文字、布局、配色、形状和箭头。
- 使用固定坐标的 draw.io XML 重建可编辑图示。
- 提供压缩文件生成与往返校验脚本。
- 适用于流程图、架构图、框图和技术示意图。

## 目录结构

```text
.
├── veusz/
│   ├── SKILL.md
│   ├── agents/
│   ├── assets/
│   │   └── default-template.vsz
│   ├── references/
│   └── scripts/
│       ├── check_veusz.py
│       ├── summarize_vsz.py
│       └── render_vsz.py
├── fig2drawio/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
│       └── make_drawio.py
└── 无害化说明.md
```

## 安装与依赖

下载或克隆本仓库，将需要的技能文件夹放入所使用 AI 工具支持的技能目录，保留文件夹内部结构。具体安装位置以对应工具的配置为准。

辅助脚本需要 **Python 3.10 或更新版本**，使用 Python 标准库。

使用 Veusz 渲染功能时，需要另行安装 [Veusz](https://veusz.github.io/)。辅助脚本依次通过以下方式查找可执行程序：

1. 命令行参数 `--veusz`
2. 环境变量 `VEUSZ_EXE`
3. 系统 `PATH` 中的 `veusz`

使用 Python 嵌入接口时，还需确保当前 Python 环境可以导入 `veusz.embed`。

查看或编辑 `.drawio` 文件，可使用 [diagrams.net](https://www.diagrams.net/) 或其桌面应用。

## 使用示例

在支持技能调用的 AI 工具中，可参考以下请求：

```text
使用 $veusz，根据提供的数据创建双面板折线图，
保留可编辑的 .vsz 项目，并导出 SVG。
```

```text
使用 $fig2drawio，将这张架构截图重建为可编辑的 .drawio 文件，
尽量保留原图的文字、配色、布局和箭头样式。
```

以下命令均在仓库根目录运行。

### 检查 Veusz 环境

```sh
python veusz/scripts/check_veusz.py
```

### 静态检查绘图项目

```sh
python veusz/scripts/summarize_vsz.py input.vsz
```

### 导出绘图项目

```sh
python veusz/scripts/render_vsz.py input.vsz output.svg --page 0
```

若 Veusz 不在系统 `PATH` 中，可通过 `--veusz` 指定其可执行程序。

### 生成 draw.io 文件

先由 AI 助手或其他工具生成 `mxGraphModel` XML，再运行：

```sh
python fig2drawio/scripts/make_drawio.py \
  --input model.xml \
  --output figure.drawio
```

该脚本负责封装、压缩和校验 XML；图片内容识别与布局重建由 AI 助手完成。

## 模板与数据安全

- Veusz 默认模板仅包含合成演示数据，不代表实验结果。
- 分享版本已移除原有的本机固定路径、私人项目标识和模板实验数据。
- 用户输入、实际数据和生成结果应保存在独立工作目录中。
- `.vsz` 是可执行脚本，运行陌生文件前应检查其内容。
- draw.io 的压缩与 Base64 编码不会隐藏敏感信息。分享图稿前，应检查文字、隐藏单元格、额外页面、属性和资源链接。
- 本地图稿优先使用本地应用预览；使用在线编辑器或外部预览服务时，应确认图稿适合上传。

本次清理内容和验证范围详见 `无害化说明.md`。

## 使用边界

图示重建的准确度受原图清晰度、文字可读性、字体和图形复杂度影响。生成后应对照原图检查文字、连接关系和布局。

Veusz 的命令行导出与图形界面可能存在字体或间距差异；对排版精度要求较高时，应检查最终导出文件。
