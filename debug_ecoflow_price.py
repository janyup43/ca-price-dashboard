#!/usr/bin/env python3
"""调试 EcoFlow 价格提取"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

test_url = "https://ca.ecoflow.com/products/delta-pro-portable-power-station"

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

print("=" * 70)
print("EcoFlow DELTA Pro 价格提取调试")
print("=" * 70)
print(f"\n测试URL: {test_url}\n")

try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()
        page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # 查找所有包含价格的元素
        price_info = page.evaluate('''() => {
            const result = [];

            // 查找所有可能包含价格的元素
            const priceElements = document.querySelectorAll('[class*="price"], [class*="Price"]');
            priceElements.forEach(el => {
                const text = (el.innerText || el.textContent || '').trim();
                if (text && (text.includes('$') || text.includes('C$'))) {
                    result.push({
                        className: el.className.substring(0, 100),
                        text: text.substring(0, 150),
                        innerHTML: el.innerHTML.substring(0, 200)
                    });
                }
            });

            return result;
        }''')

        print(f"找到 {len(price_info)} 个价格元素:\n")
        for i, info in enumerate(price_info[:30], 1):
            print(f"{i}. Class: {info['className']}")
            print(f"   Text: {info['text']}")
            print(f"   HTML: {info['innerHTML'][:100]}...")
            print()

except Exception as e:
    print(f"\n✗ 调试失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
