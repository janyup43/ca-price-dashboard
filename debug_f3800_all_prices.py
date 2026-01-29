#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from scraper_stealth import *

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

url = 'https://www.ankersolix.com/ca/products/f3800-plus?variant=44782348665028'

print("=" * 70)
print("F3800 Plus - 检查所有价格元素")
print("=" * 70)

with StealthBrowser(config) as browser:
    page = browser.get_page()
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)

    prices = page.evaluate('''() => {
        const result = [];
        const priceEls = document.querySelectorAll('[class*="price"], [class*="Price"]');
        priceEls.forEach(el => {
            const text = (el.innerText || el.textContent || '').trim();
            if (text && text.match(/\$|C\$/)) {
                result.push({
                    className: el.className.substring(0, 80),
                    text: text.substring(0, 100)
                });
            }
        });
        return result;
    }''')

    print(f'\n找到 {len(prices)} 个包含价格的元素:\n')
    for i, p in enumerate(prices[:25], 1):
        print(f"{i}. Class: {p['className']}")
        print(f"   Text: {p['text']}")
        print()
