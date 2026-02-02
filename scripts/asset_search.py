import os
import csv
import argparse
import sys

# 设置基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def search_assets(query, category=None, limit=20):
    """
    在 CSV 数据中搜索资产。
    query: 搜索关键词（支持多关键词，空格分隔）
    category: 指定 CSV 文件名（如果不指定，则搜索所有文件）
    """
    results = []
    queries = query.lower().split()
    
    files_to_search = []
    if category:
        if not category.endswith('.csv'):
            category += '.csv'
        files_to_search = [category]
    else:
        files_to_search = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

    for filename in files_to_search:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 匹配标识符或描述
                text_to_search = (row['identifier'] + " " + row['description'] + " " + row['category']).lower()
                if all(q in text_to_search for q in queries):
                    results.append(row)
                    if len(results) >= limit:
                        return results
    return results

def format_results(results):
    if not results:
        return "未找到匹配项。"
    
    output = []
    output.append(f"{'Identifier':<30} | {'Enum Type':<20} | {'Category'}")
    output.append("-" * 80)
    for r in results:
        output.append(f"{r['identifier']:<30} | {r['enum_type']:<20} | {r['category']}")
    return "\n".join(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="剪映资产搜索工具")
    parser.add_argument("query", nargs="?", default=None, help="搜索关键词")
    parser.add_argument("-c", "--category", help="限定分类 (例如: filters, text_animations)")
    parser.add_argument("-l", "--limit", type=int, default=20, help="返回结果数量限制")
    parser.add_argument("--list", action="store_true", help="列出所有可用分类及其数量")
    
    args = parser.parse_args()
    
    if args.list or args.query is None:
        # 显示分类摘要
        print("=== 剪映资产数据库概览 ===")
        print(f"{'分类文件名':<30} | {'资产数量'}")
        print("-" * 50)
        total = 0
        for filename in sorted(os.listdir(DATA_DIR)):
            if filename.endswith('.csv'):
                with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                    count = sum(1 for line in f) - 1
                    print(f"{filename:<30} | {count}")
                    total += count
        print("-" * 50)
        print(f"{'总计':<30} | {total}")
        print("\n提示: 使用 'python asset_search.py <关键词>' 进行搜索")
        sys.exit(0)

    search_results = search_assets(args.query, args.category, args.limit)
    print(format_results(search_results))
