#!/usr/bin/env python3
"""查找 Jackery 300Wh 级别产品"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

print("=" * 70)
print("查找 Jackery 300Wh 级别产品")
print("=" * 70)

try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()
        page.goto("https://www.jackery.ca/collections/portable-power-stations",
                 wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # 查找所有产品
        products = page.evaluate('''() => {
            const result = [];
            const productLinks = document.querySelectorAll('a[href*="/products/"]');

            productLinks.forEach(link => {
                const href = link.href;
                const text = link.textContent || '';

                // 查找容量信息
                const parent = link.closest('.product-item, .product-card, [class*="product"]');
                const fullText = parent ? parent.textContent : text;

                // 匹配 Wh
                const whMatch = fullText.match(/(\\d+)\\s*Wh/i);
                if (whMatch) {
                    const capacity = parseInt(whMatch[1]);

                    // 查找产品名称
                    const titleEl = parent ?
                        parent.querySelector('.product-title, [class*="title"], h3, h2') : null;
                    const title = titleEl ? titleEl.textContent.trim() : text.trim();

                    result.push({
                        title: title,
                        capacity: capacity,
                        url: href,
                        fullText: fullText.substring(0, 200)
                    });
                }
            });

            return result;
        }''')

        # 过滤 200-300 Wh 范围
        products_300 = [p for p in products if 200 <= p['capacity'] <= 300]

        # 去重
        seen_urls = set()
        unique_products = []
        for p in products_300:
            if p['url'] not in seen_urls:
                seen_urls.add(p['url'])
                unique_products.append(p)

        print(f"\n找到 {len(unique_products)} 个 200-300Wh 产品：\n")
        for i, p in enumerate(unique_products, 1):
            print(f"{i}. {p['title']}")
            print(f"   容量: {p['capacity']}Wh")
            print(f"   URL: {p['url']}")
            print()

except Exception as e:
    print(f"✗ 搜索失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
