#!/usr/bin/env python3
"""优化dashboard性能"""

import re

# 读取HTML文件
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 添加CSS性能优化 - 在</style>之前插入
css_optimization = """
        /* 性能优化 */
        .comparison-table {
            contain: layout style paint;
            will-change: contents;
        }

        .comparison-table tbody {
            backface-visibility: hidden;
            transform: translateZ(0);
        }

        .comparison-table tr {
            contain: layout style paint;
        }
"""

html = html.replace('</style>', css_optimization + '\n    </style>')

# 2. 添加性能优化的JavaScript函数 - 在renderComparison之前
js_optimization = """
        // 性能优化：防抖函数
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        // 性能优化：Amazon链接缓存
        const amazonLinkCache = new Map();

        function generateAmazonLink(productName, brand) {
            const cacheKey = productName;
            if (amazonLinkCache.has(cacheKey)) {
                return amazonLinkCache.get(cacheKey);
            }

            const urlOrAsin = amazonAsins[productName];
            let result;

            if (!urlOrAsin || urlOrAsin === 'YOUR_ASIN_HERE') {
                result = `<a href="https://www.amazon.ca/s?k=${encodeURIComponent(brand + ' ' + productName)}" target="_blank" style="color: var(--accent-orange); font-size: 0.8rem; display: block; margin-top: 3px;">Amazon Search →</a>`;
            } else {
                let amazonUrl;
                if (urlOrAsin.startsWith('http://') || urlOrAsin.startsWith('https://')) {
                    amazonUrl = urlOrAsin;
                } else if (urlOrAsin.includes('/dp/')) {
                    amazonUrl = 'https://www.amazon.ca/' + urlOrAsin;
                } else if (urlOrAsin.match(/^B[0-9A-Z]{9}$/)) {
                    amazonUrl = 'https://www.amazon.ca/dp/' + urlOrAsin;
                } else {
                    result = `<a href="https://www.amazon.ca/s?k=${encodeURIComponent(brand + ' ' + productName)}" target="_blank" style="color: var(--accent-orange); font-size: 0.8rem; display: block; margin-top: 3px;">Amazon Search →</a>`;
                    amazonLinkCache.set(cacheKey, result);
                    return result;
                }
                result = `<a href="${amazonUrl}" target="_blank" style="color: var(--accent-orange); font-size: 0.8rem; display: block; margin-top: 3px;">Amazon →</a>`;
            }

            amazonLinkCache.set(cacheKey, result);
            return result;
        }

"""

# 在 // Render comparison table 之前插入
html = html.replace('        // Render comparison table', js_optimization + '        // Render comparison table')

# 3. 优化renderComparison函数 - 替换整个Amazon链接生成部分
old_amazon_logic = r"""                            \$\(\(\) => \{
                                const urlOrAsin = amazonAsins\[p\.name\];
                                if \(\!urlOrAsin \|\| urlOrAsin === 'YOUR_ASIN_HERE'\) \{
                                    // 没有配置，使用搜索
                                    return `<a href="https://www\.amazon\.ca/s\?k=\$\{encodeURIComponent\(p\.brand \+ ' ' \+ p\.name\)\}" target="_blank" style="color: var\(--accent-orange\); font-size: 0\.8rem; display: block; margin-top: 3px;">Amazon Search →</a>`;
                                \}

                                let amazonUrl;
                                if \(urlOrAsin\.startsWith\('http://'\) \|\| urlOrAsin\.startsWith\('https://'\)\) \{
                                    // 完整URL，直接使用
                                    amazonUrl = urlOrAsin;
                                \} else if \(urlOrAsin\.includes\('/dp/'\)\) \{
                                    // 部分URL（如 Product-Title/dp/B0XXX/ref=\.\.\.），补充域名
                                    amazonUrl = 'https://www\.amazon\.ca/' \+ urlOrAsin;
                                \} else if \(urlOrAsin\.match\(/\^B\[0-9A-Z\]\{9\}\$/\)\) \{
                                    // 纯ASIN格式，使用简化链接
                                    amazonUrl = 'https://www\.amazon\.ca/dp/' \+ urlOrAsin;
                                \} else \{
                                    // 无法识别格式，fallback到搜索
                                    return `<a href="https://www\.amazon\.ca/s\?k=\$\{encodeURIComponent\(p\.brand \+ ' ' \+ p\.name\)\}" target="_blank" style="color: var\(--accent-orange\); font-size: 0\.8rem; display: block; margin-top: 3px;">Amazon Search →</a>`;
                                \}

                                return `<a href="\$\{amazonUrl\}" target="_blank" style="color: var\(--accent-orange\); font-size: 0\.8rem; display: block; margin-top: 3px;">Amazon →</a>`;
                            \}\)\(\)\}"""

new_amazon_logic = "${generateAmazonLink(p.name, p.brand)}"

html = re.sub(old_amazon_logic, new_amazon_logic, html, flags=re.MULTILINE | re.DOTALL)

# 保存优化后的文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Dashboard性能优化完成！")
print("\n优化内容:")
print("  1. 添加CSS性能优化（contain, will-change, transform）")
print("  2. 添加Amazon链接缓存，避免重复计算")
print("  3. 简化渲染逻辑，减少IIFE调用")
print("\n刷新浏览器即可看到性能提升")
