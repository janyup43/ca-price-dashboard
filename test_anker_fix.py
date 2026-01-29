#!/usr/bin/env python3
"""测试Anker价格提取修复"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

print("=" * 70)
print("测试Anker价格提取修复")
print("=" * 70)

# 测试之前失败的产品
test_urls = [
    ("F3000 (之前失败)", "https://www.ankersolix.com/ca/products/f3000?variant=44964905681092"),
    ("C2000 Gen 2 (之前失败)", "https://www.ankersolix.com/ca/products/c2000-gen2?variant=45310720639172"),
    ("F3800 Plus (之前成功)", "https://www.ankersolix.com/ca/products/f3800-plus?variant=44782348665028"),
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

            product = official_scraper._scrape_product_page(page, url, "Anker")

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
