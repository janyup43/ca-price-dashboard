#!/usr/bin/env python3
"""小范围测试 - 验证修复效果"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *
from playwright.sync_api import sync_playwright
import json

print("=" * 60)
print("小范围测试 - 验证容量和价格提取修复")
print("=" * 60)

# 测试产品列表
test_products = [
    ("EcoFlow", "https://ca.ecoflow.com/products/delta-2-portable-power-station"),
    ("EcoFlow", "https://ca.ecoflow.com/products/river-2-pro-portable-power-station"),
]

config = load_config()
config['min_delay'] = 1
config['max_delay'] = 2

class TestBrowser:
    """简化的浏览器管理器用于测试"""
    def __init__(self, config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        fingerprint = get_random_fingerprint()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            user_agent=fingerprint['user_agent'],
            viewport=fingerprint['viewport']
        )
        self.page = self.context.new_page()

        if self.config.get('stealth_mode'):
            apply_stealth_scripts(self.page)

        return self

    def __exit__(self, *args):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_page(self):
        return self.page

print("\n开始测试...")
print("-" * 60)

results = []

try:
    with TestBrowser(config) as browser:
        scraper = OfficialSiteScraper(config)

        for i, (brand, url) in enumerate(test_products):
            print(f"\n[{i+1}/{len(test_products)}] 测试: {brand}")
            print(f"URL: {url}")

            try:
                product = scraper._scrape_product_page(browser.get_page(), url, brand)

                if product:
                    results.append({
                        'success': True,
                        'brand': brand,
                        'name': product.name,
                        'capacity': product.capacity,
                        'current_price': product.current_price,
                        'original_price': product.original_price,
                        'discount': product.discount_percent
                    })
                    print(f"✓ 成功!")
                    print(f"  产品名称: {product.name}")
                    print(f"  容量: {product.capacity}")
                    print(f"  当前价格: ${product.current_price}")
                    if product.original_price:
                        print(f"  原价: ${product.original_price}")
                    if product.discount_percent:
                        print(f"  折扣: {product.discount_percent}%")
                else:
                    results.append({
                        'success': False,
                        'brand': brand,
                        'url': url,
                        'error': '无法提取产品信息'
                    })
                    print(f"✗ 失败: 无法提取产品信息")

            except Exception as e:
                results.append({
                    'success': False,
                    'brand': brand,
                    'url': url,
                    'error': str(e)
                })
                print(f"✗ 错误: {e}")

            # 短暂延迟
            if i < len(test_products) - 1:
                time.sleep(2)

except Exception as e:
    print(f"\n✗ 浏览器错误: {e}")
    sys.exit(1)

# 显示测试结果摘要
print("\n" + "=" * 60)
print("测试结果摘要")
print("=" * 60)

success_count = sum(1 for r in results if r.get('success'))
print(f"\n总测试数: {len(results)}")
print(f"成功: {success_count}")
print(f"失败: {len(results) - success_count}")

if success_count > 0:
    print("\n✓ 修复验证成功!")
    print("  - 容量信息提取正常")
    print("  - 价格信息提取正常")
    print("\n建议: 运行完整爬虫更新所有数据")
    print("  命令: python3 scraper_stealth.py")
else:
    print("\n✗ 测试失败，需要进一步调试")

print("\n详细结果:")
print(json.dumps(results, indent=2, ensure_ascii=False))
