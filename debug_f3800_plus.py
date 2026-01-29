#!/usr/bin/env python3
"""调试F3800 Plus价格提取"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

test_url = "https://www.ankersolix.com/ca/products/f3800-plus?variant=44782348665028"

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

print("=" * 70)
print("F3800 Plus价格提取调试")
print("=" * 70)
print(f"\n测试URL: {test_url}\n")

try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()
        page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # 查找所有salePrice和包含价格的元素
        price_info = page.evaluate('''() => {
            const result = [];

            // 查找salePrice
            const salePrices = document.querySelectorAll('.salePrice, [class*="salePrice"]');
            salePrices.forEach(el => {
                if (!/savePrice/i.test(el.className)) {
                    result.push({
                        type: 'salePrice',
                        className: el.className,
                        text: (el.innerText || el.textContent || '').trim()
                    });
                }
            });

            // 查找ProductTag_discountPrice
            const discountPrices = document.querySelectorAll('[class*="ProductTag_discountPrice"]');
            discountPrices.forEach(el => {
                result.push({
                    type: 'ProductTag_discountPrice',
                    className: el.className,
                    text: (el.innerText || el.textContent || '').trim()
                });
            });

            return result;
        }''')

        print(f"找到 {len(price_info)} 个价格元素:\n")
        for i, info in enumerate(price_info, 1):
            print(f"{i}. Type: {info['type']}")
            print(f"   Class: {info['className']}")
            print(f"   Text: {info['text']}")
            print()

except Exception as e:
    print(f"\n✗ 调试失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
