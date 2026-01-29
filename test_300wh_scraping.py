#!/usr/bin/env python3
"""测试 300Wh 产品抓取"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

print("=" * 70)
print("测试 300Wh 产品抓取")
print("=" * 70)

test_urls = [
    ("EcoFlow TRAIL 300 DC", "https://ca.ecoflow.com/products/trail-series"),
    ("EcoFlow RIVER 3 Plus", "https://ca.ecoflow.com/products/river-3-plus-portable-power-station"),
    ("EcoFlow RIVER 3", "https://ca.ecoflow.com/products/river-3-portable-power-station"),
]

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 3

try:
    with StealthBrowser(config) as browser:
        screenshot_mgr = ScreenshotManager()
        official_scraper = OfficialSiteScraper(config, screenshot_mgr)
        page = browser.get_page()

        for name, url in test_urls:
            print(f"\n测试: {name}")
            print(f"URL: {url}")
            print("-" * 70)

            product = official_scraper._scrape_product_page(page, url, "EcoFlow")

            if product:
                print(f"✓ 成功！")
                print(f"  品牌: {product.brand}")
                print(f"  名称: {product.name}")
                print(f"  容量: {product.capacity}")
                print(f"  当前价格: ${product.current_price}")
                if product.original_price:
                    print(f"  原价: ${product.original_price}")
                if product.discount_percent:
                    print(f"  折扣: {product.discount_percent}%")
            else:
                print("✗ 失败：无法提取产品信息")

            time.sleep(2)

except Exception as e:
    print(f"\n✗ 测试出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
