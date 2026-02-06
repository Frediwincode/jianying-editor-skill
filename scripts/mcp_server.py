
import asyncio
import os
import sys
import json
from mcp.server.fastmcp import FastMCP

# --- 1. 环境自发现 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# 优先从环境变量读取，否则使用当前脚本所在位置
skill_root = os.environ.get('JY_SKILL_ROOT', os.path.dirname(current_dir))
scripts_path = os.path.join(skill_root, ".agent", "skills", "jianying-editor", "scripts")
if not os.path.exists(scripts_path):
    # 兜底：如果项目根目录本身就是代码
    scripts_path = os.path.join(skill_root, "scripts")

if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

try:
    from jy_wrapper import JyProject
except ImportError:
    print(f"[-] Error: Could not find jy_wrapper in {scripts_path}")
    sys.exit(1)

# --- 2. 初始化 MCP Server ---
mcp = FastMCP("JianYing-Automation")

@mcp.tool()
async def create_simple_video(project_name: str, video_path: str, subtitle: str = None) -> str:
    """
    创建一个简单的视频项目，导入一段视频并可选添加字幕。
    
    Args:
        project_name: 项目名称
        video_path: 视频文件的绝对路径
        subtitle: 要在开头显示的字幕内容
    """
    try:
        jy = JyProject(project_name, overwrite=True)
        jy.add_media_safe(video_path, start_time="0s")
        if subtitle:
            jy.add_text_simple(subtitle, start_time="1s", duration="3s")
        jy.save()
        return f"Successfully created project: {project_name}. Check it in JianYing."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def smart_rough_cut(video_path: str) -> str:
    """
    对一个长视频进行智能分析并生成精彩时刻粗剪合集。
    会自动寻找具有画面冲击力的时刻（如动作变化、喂鸡等）并拼接。
    """
    # 动态导入防止循环依赖
    smart_script = os.path.join(scripts_path, "smart_rough_cut.py")
    if not os.path.exists(smart_script):
        return "Error: smart_rough_cut.py not found."
    
    # 简单调用现有的逻辑
    import subprocess
    cmd = [sys.executable, smart_script, video_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        return f"Rough cut complete. Output:\n{stdout}"
    else:
        return f"Rough cut failed.\nError: {stderr}"

@mcp.tool()
async def search_assets(query: str, category: str = "filters") -> str:
    """
    在剪映库中搜索特效、滤镜或动画的具体 IDs。
    
    Args:
        query: 搜索关键词（如 '复古', '打字机'）
        category: 类别, 可选: filters, transitions, video_effects, text_effects, animations
    """
    search_script = os.path.join(scripts_path, "asset_search.py")
    import subprocess
    cmd = [sys.executable, search_script, query, "-c", category]
    result = subprocess.check_output(cmd, text=True)
    return result

if __name__ == "__main__":
    mcp.run()
