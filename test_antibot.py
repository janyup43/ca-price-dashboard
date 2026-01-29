#!/usr/bin/env python3
"""测试反爬虫绕过方案"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *
import json

print("=" * 70)
print("反爬虫绕过测试")
print("=" * 70)

config = load_config()

# 测试Amazon（只测试前2个）
test_config = config.copy()
test_config['amazon_asins'] = config['amazon_asins'][:2]  # 只测试前2个
test_config['min_delay'] = 3
test_config['max_delay'] = 6

print("\n[测试1] Amazon反爬虫绕过 (测试2个产品)")
print("-" * 70)

with StealthBrowser(test_config) as browser:
    screenshot_mgr = ScreenshotManager()
    amazon_scraper = AmazonCanadaScraper(test_config, screenshot_mgr)

    amazon_products = amazon_scraper.scrape(browser)

    print(f"\n结果: 成功获取 {len(amazon_products)} / 2 个Amazon产品")

    if amazon_products:
        print("\n✓ Amazon反爬虫绕过成功！")
        for p in amazon_products:
            print(f"  - {p.name[:50]}")
            print(f"    价格: ${p.current_price}")
    else:
        print("\n✗ Amazon反爬虫绕过失败")

print("\n" + "=" * 70)
print("[测试2] EcoFlow列表页爬取")
print("-" * 70)

with StealthBrowser(test_config) as browser:
    screenshot_mgr = ScreenshotManager()
    official_scraper = OfficialSiteScraper(test_config, screenshot_mgr)

    page = browser.get_page()

    try:
        ecoflow_products = official_scraper._scrape_ecoflow_listing(page)

        print(f"\n结果: 成功获取 {len(ecoflow_products)} 个EcoFlow产品")

        if ecoflow_products:
            print("\n✓ EcoFlow列表页爬取成功！")
            for p in ecoflow_products:
                print(f"  - {p.name}")
                print(f"    容量: {p.capacity}, 价格: ${p.current_price}")
        else:
            print("\n✗ EcoFlow列表页爬取失败")
    except Exception as e:
        print(f"\n✗ EcoFlow测试出错: {e}")

print("\n" + "=" * 70)
print("[测试3] Anker列表页爬取")
print("-" * 70)

with StealthBrowser(test_config) as browser:
    screenshot_mgr = ScreenshotManager()
    official_scraper = OfficialSiteScraper(test_config, screenshot_mgr)

    page = browser.get_page()

    try:
        anker_products = official_scraper._scrape_anker_listing(page)

        print(f"\n结果: 成功获取 {len(anker_products)} 个Anker产品")

        if anker_products:
            print("\n✓ Anker列表页爬取成功！")
            for p in anker_products:
                print(f"  - {p.name}")
                print(f"    容量: {p.capacity}, 价格: ${p.current_price}")
        else:
            print("\n⚠ Anker列表页未获取到产品（可能需要手动更新产品URL）")
    except Exception as e:
        print(f"\n✗ Anker测试出错: {e}")

print("\n" + "=" * 70)
print("测试总结")
print("=" * 70)
print("\n建议:")
print("1. 如果Amazon测试成功，说明新的反爬虫策略有效")
print("2. 如果EcoFlow/Anker列表页成功，说明超时和滚动优化有效")
print("3. Amazon反爬虫非常强，成功率可能不是100%，这是正常的")
print("4. 建议将config中的amazon_asins减少到真正需要的产品")
print("\n" + "=" * 70)
