#!/usr/bin/env python3
"""调试Anker价格提取失败的产品"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *

print("=" * 70)
print("Anker价格提取调试工具")
print("=" * 70)

# 测试一个失败的产品
test_url = "https://www.ankersolix.com/ca/products/f3000?variant=44964905681092"

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

print(f"\n正在访问: {test_url}")
print("-" * 70)

try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()

        page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
        print("✓ 页面已加载 (domcontentloaded)")

        time.sleep(5)  # 等待更长时间
        print("✓ 已等待5秒让JavaScript加载")

        # 检查所有包含price的元素
        price_info = page.evaluate('''() => {
            const priceElements = [];

            // 查找所有可能包含价格的元素
            const selectors = [
                '[class*="price"]',
                '[class*="Price"]',
                '[data-testid*="price"]',
                '.money',
                '[data-price]'
            ];

            selectors.forEach(sel => {
                const elements = document.querySelectorAll(sel);
                elements.forEach(el => {
                    const text = (el.innerText || el.textContent || '').trim();
                    if (text) {
                        priceElements.push({
                            selector: sel,
                            className: el.className,
                            text: text.substring(0, 100),
                            id: el.id || 'no-id',
                            dataset: JSON.stringify(el.dataset)
                        });
                    }
                });
            });

            return priceElements;
        }''')

        print(f"\n找到 {len(price_info)} 个包含'price'的元素：\n")

        for i, info in enumerate(price_info, 1):
            print(f"{i}. Selector: {info['selector']}")
            print(f"   Class: {info['className']}")
            print(f"   ID: {info['id']}")
            print(f"   Text: {info['text']}")
            print(f"   Dataset: {info['dataset']}")
            print()

        # 尝试查找包含$符号的所有文本
        dollar_text = page.evaluate('''() => {
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            const texts = [];
            let node;
            while(node = walker.nextNode()) {
                const text = node.nodeValue.trim();
                if (text.includes('$') || text.includes('CA') || text.includes('CAD')) {
                    texts.push({
                        text: text,
                        parent: node.parentElement.className || 'no-class'
                    });
                }
            }
            return texts;
        }''')

        print("\n" + "=" * 70)
        print(f"找到 {len(dollar_text)} 个包含$符号的文本节点：\n")

        for i, info in enumerate(dollar_text[:20], 1):  # 只显示前20个
            print(f"{i}. Parent Class: {info['parent']}")
            print(f"   Text: {info['text']}")
            print()

        print("=" * 70)

except Exception as e:
    print(f"\n✗ 调试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n提示: 检查上面的输出，找出为什么价格提取失败")
print("-" * 70)
