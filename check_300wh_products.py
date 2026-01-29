#!/usr/bin/env python3
"""检查各品牌 300Wh 级别产品"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

print("=" * 70)
print("检查 300Wh 级别产品")
print("=" * 70)

# 检查 Jackery 列表页
print("\n检查 Jackery 产品...")
try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()
        page.goto("https://www.jackery.ca/collections/portable-power-stations",
                 wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        products = page.evaluate('''() => {
            const result = [];
            const productCards = document.querySelectorAll('.product-card, .product-item, [class*="product"]');

            productCards.forEach(card => {
                const titleEl = card.querySelector('a[href*="/products/"], h3, h2, .product-title, [class*="title"]');
                const priceEl = card.querySelector('[class*="price"]');

                if (titleEl) {
                    const title = titleEl.textContent.trim();
                    const href = titleEl.href || '';

                    // 查找包含 Wh 的文本
                    const text = card.textContent || '';
                    const whMatch = text.match(/(\\d+)\\s*Wh/i);

                    if (whMatch) {
                        const capacity = parseInt(whMatch[1]);
                        if (capacity >= 200 && capacity <= 600) {
                            result.push({
                                title: title.substring(0, 100),
                                capacity: capacity,
                                url: href,
                                price: priceEl ? priceEl.textContent.trim().substring(0, 50) : 'N/A'
                            });
                        }
                    }
                }
            });

            return result;
        }''')

        print(f"\n找到 {len(products)} 个 200-600Wh 产品：\n")
        for i, p in enumerate(products, 1):
            print(f"{i}. {p['title']}")
            print(f"   容量: {p['capacity']}Wh")
            print(f"   价格: {p['price']}")
            print(f"   URL: {p['url']}")
            print()

except Exception as e:
    print(f"✗ 检查失败: {e}")
    import traceback
    traceback.print_exc()

# 检查 EcoFlow 列表页
print("\n" + "=" * 70)
print("检查 EcoFlow 产品...")
try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()
        page.goto("https://ca.ecoflow.com/collections/portable-power-station",
                 wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        products = page.evaluate('''() => {
            const result = [];
            const productCards = document.querySelectorAll('.product-item, [class*="product"]');

            productCards.forEach(card => {
                const titleEl = card.querySelector('a[href*="/products/"]');

                if (titleEl) {
                    const title = titleEl.textContent.trim();
                    const href = titleEl.href || '';

                    // 查找包含 Wh 的文本
                    const text = card.textContent || '';
                    const whMatch = text.match(/(\\d+)\\s*Wh/i);

                    if (whMatch) {
                        const capacity = parseInt(whMatch[1]);
                        if (capacity >= 200 && capacity <= 600) {
                            result.push({
                                title: title.substring(0, 100),
                                capacity: capacity,
                                url: href
                            });
                        }
                    }
                }
            });

            return result;
        }''')

        print(f"\n找到 {len(products)} 个 200-600Wh 产品：\n")
        for i, p in enumerate(products, 1):
            print(f"{i}. {p['title']}")
            print(f"   容量: {p['capacity']}Wh")
            print(f"   URL: {p['url']}")
            print()

except Exception as e:
    print(f"✗ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
