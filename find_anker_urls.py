#!/usr/bin/env python3
"""自动查找Anker有效产品URL"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_stealth import *
import json

print("=" * 70)
print("Anker产品URL查找工具")
print("=" * 70)

config = load_config()
config['min_delay'] = 2
config['max_delay'] = 4

print("\n正在访问Anker加拿大站...")
print("URL: https://www.anker.com/ca/collections/portable-power-stations")
print("-" * 70)

anker_urls = []

try:
    with StealthBrowser(config) as browser:
        page = browser.get_page()

        # 访问列表页
        page.goto("https://www.anker.com/ca/collections/portable-power-stations",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # 滚动加载所有产品
        print("\n正在加载产品...")
        for i in range(10):
            page.evaluate('window.scrollBy(0, 800)')
            time.sleep(1)
            print(f"  滚动 {i+1}/10")

        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(3)

        print("\n提取产品链接...")

        # 提取所有产品链接
        product_data = page.evaluate('''() => {
            const products = [];
            const links = document.querySelectorAll('a[href*="/products/"]');

            links.forEach(link => {
                const href = link.href;
                const text = link.innerText || link.textContent || '';

                // 只保留包含power station/solix的产品
                if (text.toLowerCase().includes('solix') ||
                    text.toLowerCase().includes('power station') ||
                    href.toLowerCase().includes('solix') ||
                    href.toLowerCase().includes('power-station')) {

                    if (!products.find(p => p.url === href)) {
                        products.push({
                            url: href,
                            text: text.trim().substring(0, 60)
                        });
                    }
                }
            });

            return products;
        }''')

        print(f"\n找到 {len(product_data)} 个相关产品链接：\n")

        for i, p in enumerate(product_data, 1):
            print(f"{i}. {p['text']}")
            print(f"   {p['url']}\n")
            anker_urls.append(p['url'])

        # 保存到配置文件
        if anker_urls:
            config_path = 'data/config.json'
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            config_data['anker_products'] = anker_urls
            config_data['_anker_found_date'] = datetime.now().isoformat()

            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            print("=" * 70)
            print(f"✓ 已保存 {len(anker_urls)} 个Anker产品URL到配置文件")
            print("=" * 70)
        else:
            print("=" * 70)
            print("⚠ 未找到Anker产品URL")
            print("   可能原因:")
            print("   1. 页面结构已变化")
            print("   2. 需要登录才能查看")
            print("   3. 产品暂时下架")
            print("=" * 70)

except Exception as e:
    print(f"\n✗ 查找失败: {e}")
    import traceback
    traceback.print_exc()

print("\n提示:")
print("- 下次运行爬虫时将使用这些新URL")
print("- 如需手动添加URL，请编辑 data/config.json 中的 anker_products")
print("-" * 70)
