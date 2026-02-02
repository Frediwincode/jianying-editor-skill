import os
import csv
import argparse
import sys

# 设置基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# --- 扩展: 常见同义词映射库 ---
# 用于反向推导 Enum Key
EFFECT_SYNONYMS = {
    "typewriter": ["打字机", "字幕", "typing", "复古打字机"],
    "fade": ["渐隐", "渐显", "黑场", "白场", "fade_in", "fade_out"],
    "glitch": ["故障", "干扰", "燥波", "雪花"],
    "zoom": ["拉近", "拉远", "缩放", "变焦"],
    "shake": ["振动", "摇晃", "抖动"],
    "blur": ["模糊", "虚化"],
    "glow": ["发光", "辉光", "霓虹"],
    "retro": ["复古", "胶片", "怀旧", "DV"],
    "dissolve": ["叠化", "溶解", "混合"],
}

SYNONYMS = {
    # 常用英文 -> 中文
    "dissolve": ["叠化", "溶解", "混合"],
    "fade": ["渐隐", "渐显", "黑场", "白场"],
    "glitch": ["故障", "干扰", "燥波", "雪花"],
    "zoom": ["拉近", "拉远", "缩放", "变焦"],
    "shake": ["振动", "摇晃", "抖动"],
    "blur": ["模糊", "虚化"],
    "glow": ["发光", "辉光", "霓虹"],
    "retro": ["复古", "胶片", "怀旧", "DV"],
    "film": ["胶片", "电影", "颗粒"],
    "typewriter": ["打字机", "字幕"],
    "particle": ["粒子", "碎片"],
    "fire": ["火", "燃烧", "烈焰"],
    "rain": ["雨", "水滴"],
    "cyber": ["赛博", "科技", "数码"],
    "scan": ["扫描", "全息"],
    
    # 场景化描述
    "tech": ["科技", "全息", "扫描", "数据"],
    "memory": ["回忆", "黑白", "泛黄", "柔光"],
    "horror": ["恐怖", "惊悚", "暗黑", "血"],
    "happy": ["欢乐", "跳动", "弹力"],
}

def expand_query_with_synonyms(query):
    """扩展查询词"""
    terms = query.lower().split()
    expanded_terms = set(terms)
    for term in terms:
        if term in SYNONYMS:
            expanded_terms.update(SYNONYMS[term])
        else:
            for key, values in SYNONYMS.items():
                if term in key:
                    expanded_terms.update(values)
    return list(expanded_terms)

def get_enum_key_from_ident(ident):
    """尝试从中文标识符反推英文 Enum Key"""
    ident_lower = ident.lower()
    for key, synonyms in EFFECT_SYNONYMS.items():
        if key in ident_lower: return key
        for syn in synonyms:
            if syn in ident_lower:
                return key
    return ""

def search_assets(query, category=None, limit=20):
    """搜索资产"""
    results = []
    search_terms = expand_query_with_synonyms(query)
    
    files_to_search = []
    if category:
        if not category.endswith('.csv'): category += '.csv'
        files_to_search = [category]
    else:
        if os.path.exists(DATA_DIR):
            files_to_search = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        else:
            print(f"❌ Error: Data directory not found at {DATA_DIR}")
            return []

    for filename in files_to_search:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath): continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                target_text = (row.get('identifier', '') + " " + 
                               row.get('description', '') + " " + 
                               row.get('category', '')).lower()
                
                score = 0
                if query.lower() in target_text: score += 100
                for term in search_terms:
                    if term in target_text: score += 10
                
                if score > 0:
                    row['score'] = score
                    row['source_file'] = filename
                    results.append(row)

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]

def format_results(results):
    if not results:
        return "❌ 未找到匹配项。尝试使用更简单的中文关键词。"
    
    output = []
    # 明确告诉 Agent: 这些中文名就是可以直接用的 ID
    header = f"{'Identifier':<25} | {'Category':<15} | {'API Key (Use This)':<20} | {'Source'}"
    output.append(header)
    output.append("-" * len(header))
    
    for r in results:
        ident = r.get('identifier', 'N/A')
        display_ident = ident
        if len(display_ident) > 23: display_ident = display_ident[:20] + "..."
        
        cat = r.get('category', 'N/A')[:15]
        src = r.get('source_file', '').replace('.csv', '')
        
        enum_key = get_enum_key_from_ident(ident)
        if not enum_key:
            enum_key = ident  # Fallback to Chinese Key
        
        if len(enum_key) > 18: enum_key = enum_key[:15] + "..."

        output.append(f"{display_ident:<25} | {cat:<15} | {enum_key:<20} | {src}")
        
    return "\n".join(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="剪映资产搜索工具 (智能双语版)")
    parser.add_argument("query", nargs="?", default=None, help="搜索关键词")
    parser.add_argument("-c", "--category", help="限定分类")
    parser.add_argument("-l", "--limit", type=int, default=20, help="数量限制")
    parser.add_argument("--list", action="store_true", help="列出分类")
    
    args = parser.parse_args()
    
    if args.list:
        print("=== 剪映资产数据库概览 ===")
        if os.path.exists(DATA_DIR):
            for filename in sorted(os.listdir(DATA_DIR)):
                if filename.endswith('.csv'):
                    with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                        print(f"{filename:<30} | {sum(1 for line in f) - 1}")
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(0)

    print(f"🔍 Searching for '{args.query}' (Smart Synonyms Enabled)...")
    search_results = search_assets(args.query, args.category, args.limit)
    print(format_results(search_results))
