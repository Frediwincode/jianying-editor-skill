import os
import sys
import json
from pathlib import Path

"""
视频深度分析与提取模板 (V5 规范版)
功能：使用 Antigravity API 对长视频进行视觉理解，并导出标准的故事版 JSON。
"""

# --- 1. 环境初始化 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# 自动定位 Antigravity API 技能路径
# 假设脚本在 .agent/skills/jianying-editor/references 下，向上三级寻找 API 技能
api_skill_libs = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), ".agent", "skills", "antigravity-api-skill", "libs")
if os.path.exists(api_skill_libs):
    sys.path.append(api_skill_libs)

try:
    from api_client import AntigravityClient
except ImportError:
    print("❌ Error: 找不到 api_client。请确保已安装 antigravity-api-skill 技能。")
    sys.exit(1)

def analyze_video_to_storyboard(video_path, output_json="storyboard.json", custom_prompt=None):
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return

    # 默认影视解说 Prompt
    default_prompt = """
请分析视频内容，制作一个短视频解说方案。
1. **筛选素材**：挑选 8-12 个高光片段。
2. **解说片段**：配上简短有力的解说词（必须用标点分段）。
3. **原声片段**：人物对话或高阶情绪片段，text字段留空。
严格输出为 JSON 数组：
[
  {"start": "HH:MM:SS", "duration": 5, "text": "解说词..."}
]
"""
    prompt = custom_prompt or default_prompt
    
    client = AntigravityClient()
    messages = [{"role": "user", "content": prompt}]
    
    print(f"[*] 正在分析视频: {os.path.basename(video_path)} (这可能需要几分钟)...")
    
    try:
        # 使用具备长视频理解能力的模型
        response = client.chat_completion(messages, model="gemini-3-pro", file_paths=[video_path])
        
        if not response or response.status_code != 200:
            print(f"[-] AI 请求失败: {response.status_code if response else 'No Response'}")
            return

        print("\n" + "="*30 + " AI 分析中 " + "="*30)
        full_content = ""
        for line in response.iter_lines():
            if not line: continue
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                if data_str.strip() == "[DONE]": break
                try:
                    data = json.loads(data_str)
                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        full_content += content
                except: pass
        print("\n" + "="*71)
        
        # 清洗并保存 JSON
        clean_json = full_content.strip()
        if clean_json.startswith("```"):
            clean_json = re.sub(r'^```[a-z]*\n', '', clean_json)
            clean_json = re.sub(r'\n```$', '', clean_json)
        
        with open(output_json, "w", encoding="utf-8") as f:
            f.write(clean_json)
        print(f"✅ 故事版已导出至: {output_json}")
        
    except Exception as e:
        print(f"❌ 分析出错: {e}")

if __name__ == "__main__":
    # 示例用法
    # analyze_video_to_storyboard("my_movie.mp4")
    pass
