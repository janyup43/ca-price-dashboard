#!/usr/bin/env python3
"""快速测试Amazon - 只测试1个产品"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

print("=" * 60)
print("Amazon快速测试 - 测试1个产品")
print("=" * 60)

config = load_config()
config['amazon_asins'] = ['B0BQPV1RSR']  # Jackery Explorer 1000 Plus
config['min_delay'] = 2
config['max_delay'] = 4

print("\n开始测试...")
print(f"ASIN: {config['amazon_asins'][0]}")
print("-" * 60)

try:
    with StealthBrowser(config) as browser:
        screenshot_mgr = ScreenshotManager()
        amazon_scraper = AmazonCanadaScraper(config, screenshot_mgr)

        products = amazon_scraper.scrape(browser)

        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)

        if products:
            print(f"\n✓ 成功！获取到 {len(products)} 个产品\n")
            for p in products:
                print(f"品牌: {p.brand}")
                print(f"名称: {p.name}")
                print(f"容量: {p.capacity}")
                print(f"当前价格: ${p.current_price}")
                if p.original_price:
                    print(f"原价: ${p.original_price}")
                if p.discount_percent:
                    print(f"折扣: {p.discount_percent}%")
                print(f"URL: {p.url}")
        else:
            print("\n✗ 失败：未能获取产品信息")
            print("   这可能是因为:")
            print("   1. Amazon的反爬虫机制检测到了请求")
            print("   2. 产品不可用或ASIN错误")
            print("   3. 页面结构发生了变化")

except Exception as e:
    print(f"\n✗ 测试出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
