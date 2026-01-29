#!/usr/bin/env python3
"""测试 Anker C800 价格提取"""

from playwright.sync_api import sync_playwright
import time

def test_c800():
    url = "https://www.ankersolix.com/ca/products/c800?variant=44782346830020&ref=power-stations-collection"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()

        print(f"访问: {url}")
        page.goto(url, wait_until='networkidle', timeout=60000)
        time.sleep(3)

        # 截图
        page.screenshot(path='c800_page.png')
        print("截图已保存: c800_page.png")

        # 查找所有价格相关的元素
        print("\n=== 查找价格元素 ===")

        # 尝试多种选择器
        selectors = [
            '.product-price',
            '.price',
            '[data-price]',
            '.money',
            'span[class*="price"]',
            'div[class*="price"]',
            'p[class*="price"]'
        ]

        for selector in selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"\n选择器: {selector}")
                    for i, elem in enumerate(elements[:5]):  # 只显示前5个
                        text = elem.inner_text().strip()
                        if text:
                            print(f"  [{i+1}] {text}")
            except:
                pass

        # 获取页面的所有文本，搜索价格模式
        print("\n=== 搜索价格模式 ($数字) ===")
        page_text = page.inner_text('body')
        import re
        prices = re.findall(r'\$[\d,]+(?:\.\d{2})?', page_text)
        unique_prices = list(dict.fromkeys(prices))[:10]  # 去重并取前10个
        for price in unique_prices:
            print(f"  {price}")

        input("\n按回车键关闭浏览器...")
        browser.close()

if __name__ == '__main__':
    test_c800()
