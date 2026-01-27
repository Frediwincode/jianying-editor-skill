# JianYing Editor Skill for Antigravity
![封面图](assets/readme_assets/cover.png)

这是一个为 Google Antigravity 设计的专业级 Skill，旨在通过 AI 代理全自动生成、编辑和导出剪映（JianYing/CapCut 中国版）视频草稿。

## 🚀 快速开始 (Quick Start)

### 1. 安装 Skill
请在您的项目根目录下，打开终端 (Terminal) 运行以下命令：
```bash
git clone https://github.com/luoluoluo22/jianying-editor-skill.git .agent/skills/jianying-editor
```

### 2. 在 AI 对话中使用
安装完成后，直接对您的 AI 助手说：
```text
@jianying-editor 帮我用 assets 里的视频创建一个自动剪辑项目
```

---

## 🌟 核心特性

- **多轨管理**：就像专业剪辑软件一样，支持视频、音频、字幕、贴纸、特效无限叠加。
- **高级剪辑**：支持关键帧（让画面动起来）、倍速变速、蒙版裁剪。
- **自动导出**：内置自动化脚本，支持一键导出 1080P/4K 视频（解放双手）。
- **智能变焦**：独家的 Smart Zoom 功能，能把普通的录屏自动变成“带镜头感”的演示视频。
- **开箱即用**：自带演示素材，安装好就能立马测试。

## 📦 环境准备 (必读)

为了让 Skill 正常工作，您需要在本地电脑上做一点点准备：

### 1. 安装 Python 依赖
此 Skill 的自动导出功能需要一个自动化库。请在终端运行：
```bash
pip install uiautomation
```

### 2. 确认剪映安装位置
Skill 默认认为您的剪映安装在 C 盘默认位置：
`C:\Users\Administrator\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft`

**如果您的剪映安装在 D 盘或其他位置**，请在使用时直接告诉 AI：
> "我的剪映草稿目录在 D:\JianyingPro\..."

## 📂 文件夹说明

- `SKILL.md`: 给 AI 看的说明书。
- `references/`: 剪映代码库的参考文档。
- `tools/recording/`: **录屏神器**，都在这里面。
- `assets/`: 演示用的测试视频和音乐。

## ⚠️ 常见问题 (FAQ)

1. **看不到新生成的草稿？**
   剪映软件不会实时刷新文件列表。生成草稿后，请**重启剪映**，或者随便点进一个旧草稿再退出来，就能看到新的了。

2. **自动导出失败？**
   自动导出脚本模拟了鼠标键盘操作。
   - 运行导出时，请**不要**动鼠标和键盘。
   - 目前仅支持 **剪映 5.9 或更早版本** (新版本弹窗太多容易干扰脚本)。

## 🔄 如何更新 (Update)

当有新功能发布时，您可以输入以下命令一键更新：

```bash
cd .agent/skills/jianying-editor
git pull
```

## �📅 更新日志 (Changelog)

### v1.2 (2026-01-27)
- **Smart Zoom 智能变焦**: 新增 `smart_zoomer.py`，支持基于操作录制的自动镜头推拉。
  - **动态跟随**: 当鼠标移出当前视野时，镜头会自动平滑跟随。
  - **交互反馈**: 自动在点击位置添加红圈标记。
  - **智能倒计时**: 鼠标移动会自动重置缩放停留时间，操作更流畅。
- **Recorder V3**: 录屏工具升级为 `recorder.py`。
  - 支持录制后一键调用 Wrapper 生成剪映草稿。
  - 自动管理录制文件到 `recordings/` 目录。
  - 修复了连续录制无需重启的问题。

---
Developed by Antigravity Agent Lab.
