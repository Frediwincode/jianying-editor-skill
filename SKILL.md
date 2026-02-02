---
name: jianying-editor
description: 使用 pyJianYingDraft 库自动化创建、编辑和管理剪映 (JianYing) 视频草稿。支持多轨道、动画、特效、关键帧、模板替换、字幕导出/导入、自动导出以及启动录屏工具。
---

# JianYing Editor Skill

## 目标
将 `pyJianYingDraft` 库的所有能力封装为可直接调用的执行单元，实现从素材输入到视频导出的全链路自动化。

## 核心架构
本 Skill 包含完整的项目参考手册和核心逻辑脚本：
- **`references/`**: 包含项目的 `README.md` 和核心模块（`script_file.py`, `draft_folder.py`）的接口定义，以及以下模板：
    - **`movie_commentary_template.py`**: 影视解说全自动模板（剪辑逻辑）。
    - **`video_analysis_template.py`**: 视频 AI 深度分析模板（提取逻辑）。
    - **`full_feature_showcase.py`**: (NEW) 全面功能演示脚本，涵盖剪辑、特效、关键帧及自动分层字幕。
- **`data/`**: (NEW) 结构化的资产数据库（CSV 格式），包含数千条动画、特效、滤镜和转场标识符。
- **`scripts/`**: 封装了常用的批处理任务和高效的资产搜索脚本：
    - **`asset_search.py`**: 资产搜索引擎，支持通过关键词快速检索 ID。
- **`tools/recording/`**: 专业录屏工具集，核心为 `recorder.py`，支持中文 GUI、音视频同步录制及用户操作轨迹采集（events.json）。
- **`assets/`**: 包含演示用的测试素材（assets/readme_assets/tutorial/ 下有 video.mp4, audio.mp3 等），Agent 在创建 Demo 时**必须**优先使用这些素材，而非生成纯文本草稿。

## 操作指南 (推荐使用 Wrapper)
在执行任务时，强烈推荐使用封装好的 `jy_wrapper` 来简化操作：

### 1. 引入 Wrapper
```python
import sys
import os
# 自动定位 Skill 路径并注入
skill_root = os.path.abspath(".agent/skills/jianying-editor")
sys.path.append(os.path.join(skill_root, "scripts"))
from jy_wrapper import JyProject
```

### 2. 标准工作流
```python
# 初始化 (自动探测路径 + 自动处理同名覆盖)
project = JyProject("MyAutoVideo")

# 添加媒体 (智能分流：无需指定 track_type，自动识别视频/音频后缀)
project.add_media_safe(r"C:\video.mp4", start_time="0s", duration="5s")
project.add_media_safe(r"C:\bgm.mp3", start_time="0s", track_name="BGM_Track")

# 添加文本 (扁平化参数，支持自动分层防止重叠)
# 注意：位置控制请使用 transform_y (0.0=中心, -1.0=底部, 1.0=顶部) 而非 position
project.add_text_simple("Hello Antigravity", start_time="1s", duration="3s", 
                        font_size=20.0, color_rgb=(1.0, 0.0, 0.0), 
                        transform_y=-0.8, anim_in="复古打字机")

# 保存 (内置自动错误检查与部分自愈)
project.save()
```

## 核心能力：生成式剪辑 (Generative Editing)
本 Skill 不依赖死板的模板，而是要求 Agent 像一个**人类剪辑师**一样思考。当用户提出模糊需求（如“做一个赛博朋克风格的视频”）时，请遵循以下**思维链 (Chain of Thought)**：

1.  **概念拆解 (Deconstruct)**:
    *   *Agent 思考*: "赛博朋克" = 霓虹色 (Neon) + 故障风 (Glitch) + 科技感 (Tech) + 快节奏 (Fast).
2.  **语义检索 (Semantic Search)**:
    *   使用 `asset_search.py` 搜索拆解出的关键词。
    *   `python .../asset_search.py "故障 霓虹" -c filters` -> 找到 `复古DV`, `故障_III`.
    *   `python .../asset_search.py "科技 扫描" -c transitions` -> 找到 `全息扫描`.
3.  **动态组合 (Compose)**:
    *   在 `JyProject` 代码中将通过 ID 组合起来，构建出独一无二的草稿。

### 资产检索引擎
不要猜测资产 ID，始终先搜索验证：
```bash
python .agent/skills/jianying-editor/scripts/asset_search.py "<关键词>" [-c 分类]
```
分类代码：`filters` (滤镜), `video_scene_effects` (特效), `transitions` (转场), `text_animations` (文字动画).

## CLI 诊断与快速使用
Skill 的 Wrapper 脚本支持通过命令行进行诊断和草稿管理：
```bash
# 检查剪映路径和依赖 (会输出当前探测到的草稿目录)
python .agent/skills/jianying-editor/scripts/jy_wrapper.py check

# 列出用户当前的所有剪映草稿 (按时间排序)
python .agent/skills/jianying-editor/scripts/jy_wrapper.py list-drafts

# 列出可用的枚举资产 (动画、特效、转场)
python .agent/skills/jianying-editor/scripts/jy_wrapper.py list-assets --type anim

# 快速创建草稿
python .agent/skills/jianying-editor/scripts/jy_wrapper.py create --name "Test" --media "C:/video.mp4" --text "Demo"

# 导出字幕为 SRT (保留时间轴，默认输出到项目根目录)
python .agent/skills/jianying-editor/scripts/jy_wrapper.py export-srt --name "MyProject"

# 导入 SRT 字幕到草稿 (样式与剪映默认字幕一致)
python .agent/skills/jianying-editor/scripts/jy_wrapper.py import-srt --name "MyProject" --srt "subs.srt"
# 可选参数: --track "轨道名" --clear (导入前清除现有文本轨道)

# 使用 GUI 录屏助手 (自动按时间戳命名，含声音和行为采集)
python .agent/skills/jianying-editor/tools/recording/recorder.py
```

## 约束提示
- **必须**使用 `DraftFolder` 以保证剪映能识别草稿。
- **UI 刷新**：生成后需提醒用户重启剪映或进出草稿以强制刷新。
- **导出限制**：自动导出功能仅支持剪映 V6 及以下版本。

## 推荐 AI 提示词 (解说生成)
当用户需要**全自动生成影视解说短片**时，请使用以下 prompt 模板发送给视频理解模型 (如 Gemini 3 Pro/Flash)：

```markdown
请分析视频内容，制作一个 60 秒的短视频解说方案。

### 角色设定
你是一位拥有百万粉丝的影视解说博主，擅长用犀利、幽默且带有悬念的语言快速抓住观众眼球。

### 任务要求
1. **筛选素材**：从视频中挑选 8-12 个最关键、最能推动剧情的高光片段。
2. **混合剪辑模式**：
   - **解说片段**：用于推进剧情，需要配上简短、有力的解说词。**请务必使用标点符号（逗号/句号）将长句拆分为短句，以便脚本自动断句，避免出现过长的字幕。**
   - **原声片段**：用于展示角色的情绪爆发、经典台词或关键转折，此片段**不需要解说词，最好是有人物对话的片段**（text字段留空），保留视频原声以增强沉浸感。
3. **时长控制**：片段总时长默认为 60 秒（或遵循用户指定时长）。

### 输出格式
严格输出为 JSON 数组，无需Markdown代码块标记：
[
  {
    "start": "HH:MM:SS",   // 片段开始时间
    "duration": 5,         // 片段持续秒数 (建议 3-8 秒)
    "text": "这里写解说词，用标点断句"  // 如果是原声片段，请保持此字段为 空字符串
  },
  ...
]
```
## 进阶案例: 全自动影视解说
本 Skill 提供了一个专门针对影视解说场景的参考脚本：`references/movie_commentary_template.py`。
当用户需要从长视频生成解说短片时，Agent 应参考该脚本实现以下高级功能：
1.  **分解字幕与遮罩**：自动在该片段底部添加黑色遮罩以覆盖原视频硬字幕。
2.  **双轨增强 (HighlightTrack)**：对于无解说的原声片段，自动在上方轨道复制一份，方便用户保留人物对话原声。
3.  **智能断句**：自动根据文案中的标点符号拆分字幕时间轴。
