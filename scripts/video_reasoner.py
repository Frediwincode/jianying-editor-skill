import os
import csv
import json
import argparse
import sys

# 设置基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REASONING_FILE = os.path.join(DATA_DIR, "video-reasoning.csv")

def get_video_reasoning(category_query):
    """
    根据视频类别获取设计方案
    """
    if not os.path.exists(REASONING_FILE):
        return None
        
    with open(REASONING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if category_query.lower() in row['Category'].lower():
                return row
    return None

def find_best_assets(vibe_str, category_filename):
    """
    辅助函数：根据推荐的 Vibe 到资产库中搜寻几个具体的、可用的资产 ID
    """
    from asset_search import search_assets
    search_terms = vibe_str.replace('/', ' ').split(' ')
    results = []
    for term in search_terms:
        if len(term) < 2: continue
        asset_res = search_assets(term, category=category_filename, limit=2)
        results.extend([r['identifier'] for r in asset_res])
    return list(set(results))[:5] # 返回前5个不重复的

def generate_report(category):
    reasoning = get_video_reasoning(category)
    if not reasoning:
        return f"未找到关于 '{category}' 的剪辑推理规则。"

    # 尝试查找具体的建议资产
    suggested_filters = find_best_assets(reasoning['Filter_Vibe'], "filters")
    suggested_effects = find_best_assets(reasoning['Key_Effects'], "video_scene_effects")
    suggested_transitions = find_best_assets(reasoning['Transition_Style'], "transitions")

    report = [
        f"=== {reasoning['Category']} 视频剪辑设计系统 ===",
        f"【核心逻辑】: {reasoning['Editing_Pattern']}",
        f"【画面风格】: {reasoning['Filter_Vibe']} (推荐 ID: {', '.join(suggested_filters)})",
        f"【关键特效】: {reasoning['Key_Effects']} (推荐 ID: {', '.join(suggested_effects)})",
        f"【转场风格】: {reasoning['Transition_Style']} (推荐 ID: {', '.join(suggested_transitions)})",
        f"【字体排版】: {reasoning['Typography']}",
        f"【建议比例】: {reasoning['Ratio']}",
        f"【避雷禁忌】: {reasoning['Anti_Patterns']}",
    ]
    return "\n".join(report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="视频剪辑风格推理引擎")
    parser.add_argument("category", help="视频类别 (例如: 美食, 科技, 解说)")
    
    args = parser.parse_args()
    
    # 将项目路径加入 sys.path 以便于从 asset_search 导入
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    print(generate_report(args.category))
