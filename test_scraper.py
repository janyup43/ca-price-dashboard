#!/usr/bin/env python3
"""快速测试爬虫修复"""

import sys
import json

# 检查数据文件
print("=" * 50)
print("检查当前数据文件...")
print("=" * 50)

try:
    with open('data/prices.json', 'r') as f:
        data = json.load(f)

    print(f"\n总产品数: {len(data['products'])}")

    # 按品牌统计
    brands = {}
    capacity_na = 0
    for p in data['products']:
        brand = p['brand']
        brands[brand] = brands.get(brand, 0) + 1
        if p.get('capacity') == 'N/A':
            capacity_na += 1

    print("\n品牌分布:")
    for brand, count in sorted(brands.items()):
        print(f"  {brand}: {count} 个产品")

    print(f"\n容量缺失的产品: {capacity_na} 个")

    # 显示问题产品
    print("\n=" * 50)
    print("问题产品列表:")
    print("=" * 50)

    for p in data['products']:
        if p.get('capacity') == 'N/A' or 'Oops' in p.get('name', ''):
            print(f"\n品牌: {p['brand']}")
            print(f"  名称: {p['name']}")
            print(f"  容量: {p.get('capacity', 'N/A')}")
            print(f"  价格: ${p.get('current_price')}")
            print(f"  URL: {p.get('url')}")

    print("\n=" * 50)
    print("建议:")
    print("=" * 50)
    print("1. 运行 'python3 scraper_stealth.py' 重新爬取数据")
    print("2. Anker产品URL已失效，需要访问以下网址查找新链接:")
    print("   https://www.anker.com/ca/collections/portable-power-stations")
    print("3. 修复后，价格应该会正常显示")

except FileNotFoundError:
    print("错误: 找不到 data/prices.json 文件")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"错误: JSON解析失败 - {e}")
    sys.exit(1)
