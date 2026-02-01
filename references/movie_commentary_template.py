import os
import sys
import json
import re

"""
影视解说全自动剪辑参考脚本 (V5 规范版)
功能：加载 AI 生成的故事版 JSON，自动完成视频切片、字幕遮罩、双轨原声增强。
"""

# --- 1. 环境初始化 ---
# 这里使用相对路径，确保在不同环境下都能正确定位 Skill 脚本
current_dir = os.path.dirname(os.path.abspath(__file__))
# 假设脚本放在 skill 的 examples 目录下
skill_root = os.path.dirname(os.path.dirname(current_dir)) 
# 如果是在项目根目录运行，请使用以下注入逻辑
if not os.path.exists(os.path.join(current_dir, "pyJianYingDraft")):
    skill_scripts = os.path.join(skill_root, ".agent", "skills", "jianying-editor", "scripts")
    if os.path.exists(skill_scripts):
        sys.path.append(skill_scripts)

try:
    from jy_wrapper import JyProject, draft
except ImportError:
    print("❌ Error: 找不到 jy_wrapper。请确保已正确导入 jianying-editor 技能。")
    sys.exit(1)

def build_movie_commentary(video_path, storyboard_path, project_name="AI_Auto_Commentary", bgm_path=None, mask_path=None):
    print(f"🎬 开始构建解说视频: {project_name}")
    
    # --- 2. 加载数据 ---
    if not os.path.exists(storyboard_path):
        print(f"❌ 错误: 找不到故事版文件 {storyboard_path}")
        return

    with open(storyboard_path, 'r', encoding='utf-8') as f:
        storyboard = json.load(f)

    # --- 3. 初始化项目 ---
    project = JyProject(project_name, overwrite=True)
    timeline_cursor = 0 # 微秒单位

    # --- 4. 循环处理片段 ---
    for i, scene in enumerate(storyboard):
        start_str = scene['start']
        duration = scene['duration']
        text = scene.get('text', '').strip()
        
        # 兼容处理时间格式 (HH:MM:SS 或 MM:SS)
        parts = list(map(int, start_str.split(':')))
        if len(parts) == 2: src_start_us = (parts[0] * 60 + parts[1]) * 1000000
        else: src_start_us = (parts[0] * 3600 + parts[1] * 60 + parts[2]) * 1000000
            
        duration_us = int(duration * 1000000)
        
        # A. 添加主视频片段 (MainTrack)
        project.add_media_safe(video_path, timeline_cursor, duration_us, "MainTrack", source_start=src_start_us)

        if text:
            # --- 解说片段逻辑 ---
            # B. 字幕遮罩 (强制底部)
            if mask_path and os.path.exists(mask_path):
                from pyJianYingDraft import VideoMaterial, VideoSegment, trange, ClipSettings
                mask_mat = VideoMaterial(mask_path)
                mask_seg = VideoSegment(
                    mask_mat,
                    target_timerange=trange(timeline_cursor, duration_us),
                    source_timerange=trange(0, duration_us),
                    clip_settings=ClipSettings(transform_y=-0.85)
                )
                project._ensure_track(draft.TrackType.video, "MaskTrack")
                project.script.add_segment(mask_seg, "MaskTrack")

            # C. 智能字幕 (剥离标点)
            split_pattern = r'([，。！？；：,.!?])'
            parts = re.split(split_pattern, text)
            sub_segments = [p for p in parts if p and p not in "，。！？；：,.!?"]
            
            if sub_segments:
                sub_dur_us = duration_us // len(sub_segments)
                local_cursor = timeline_cursor
                for sub_t in sub_segments:
                    display_text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', sub_t).strip()
                    if display_text:
                        project.add_text_simple(display_text, local_cursor, sub_dur_us, transform_y=-0.8)
                    local_cursor += sub_dur_us
        else:
            # --- 原声高光片段逻辑 ---
            # D. 双轨增强 (HighlightTrack)
            project.add_media_safe(video_path, timeline_cursor, duration_us, "HighlightTrack", source_start=src_start_us)

        timeline_cursor += duration_us

    # --- 5. 装饰与保存 ---
    if bgm_path and os.path.exists(bgm_path):
        project.add_audio_safe(bgm_path, 0, timeline_cursor, "BGM_Track")

    project.save()
    print(f"✅ 生成完毕！草稿名称: {project_name}")

if __name__ == "__main__":
    # 示例用法 (Agent 在执行时应根据实际路径填充变量)
    # build_movie_commentary(
    #     video_path="input_video.mp4", 
    #     storyboard_path="storyboard.json", 
    #     bgm_path="background.mp3",
    #     mask_path="mask.png"
    # )
    pass
