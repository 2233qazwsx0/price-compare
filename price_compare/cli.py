#!/usr/bin/env python3
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from price_compare.engine import PriceCompareEngine


def main():
    parser = argparse.ArgumentParser(
        description="电商商品价格自动化采集与对比工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m price_compare.cli 手机
  python -m price_compare.cli "蓝牙耳机" -p jd taobao
  python -m price_compare.cli 笔记本 -n 10 -o result.json
  python -m price_compare.cli 平板 --json
        """,
    )
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("-p", "--platforms", nargs="+", choices=["jd", "taobao", "pdd"],
                        help="指定平台 (默认全部)")
    parser.add_argument("-n", "--max-items", type=int, default=20,
                        help="每个平台最大采集数 (默认20)")
    parser.add_argument("-o", "--output", help="输出JSON文件路径")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    parser.add_argument("--quiet", action="store_true", help="静默模式，仅输出文件路径")

    args = parser.parse_args()

    platform_map = {"jd": "京东", "taobao": "淘宝", "pdd": "拼多多"}
    platforms = [platform_map[p] for p in args.platforms] if args.platforms else None

    if not args.quiet and not args.json:
        print(f"\n🔍 正在搜索: {args.keyword}", file=sys.stderr)
        if platforms:
            print(f"   平台: {', '.join(platforms)}", file=sys.stderr)
        else:
            print(f"   平台: 京东, 淘宝, 拼多多", file=sys.stderr)
        print(f"   每平台最多: {args.max_items} 条\n", file=sys.stderr)

    engine = PriceCompareEngine(platforms=platforms)

    if not args.quiet and not args.json:
        for scraper in engine.scrapers:
            print(f"  📡 正在采集 {scraper.platform_name} ...", file=sys.stderr)

    result = engine.search(args.keyword, max_items_per_platform=args.max_items)

    if not args.quiet and not args.json:
        print(f"\n  ✅ 采集完成: 原始 {result['raw_count']} 条 → 清洗后 {result['cleaned_count']} 条\n", file=sys.stderr)

    if args.json:
        output = {
            "keyword": result["keyword"],
            "statistics": result["statistics"],
            "products": [p.to_dict() for p in result["products"]],
            "comparison": result["comparison"],
            "chart_data": result["chart_data"],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.output:
        path = engine.search_to_json(args.keyword, args.output, args.max_items)
        if not args.quiet:
            print(f"  💾 结果已保存至: {path}")
    else:
        report = engine.search_to_report(args.keyword, args.max_items)
        print(report)


if __name__ == "__main__":
    main()
