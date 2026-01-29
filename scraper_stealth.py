#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版PPS价格监控爬虫 - 反反爬虫版本
支持: Jackery, EcoFlow, Anker, Amazon Canada

技术栈:
- playwright-stealth: 隐藏自动化特征
- 随机延迟: 模拟人类行为
- 代理轮换: 防止IP封禁
- 浏览器指纹伪装: 绑过指纹检测

⚠️ 风险提示:
- 仅供个人使用，请勿商业化
- 控制请求频率，建议每天1-2次
- 可能违反网站ToS
"""

import json
import os
import re
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from playwright.sync_api import sync_playwright, Page, BrowserContext

# ============================================
# 配置区域
# ============================================

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PRICES_FILE = os.path.join(DATA_DIR, 'prices.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
SCREENSHOTS_FILE = os.path.join(DATA_DIR, 'screenshots.json')
SCREENSHOTS_DIR = os.path.join(DATA_DIR, 'screenshots')

# 默认配置
DEFAULT_CONFIG = {
    # 代理配置 (可选，格式: "http://user:pass@host:port" 或 "http://host:port")
    "proxies": [],

    # Amazon产品ASIN列表 (加拿大站)
    "amazon_asins": [
        "B0BQPV1RSR",  # Jackery Explorer 1000 Plus
        "B0D1DFXS7L",  # Jackery Explorer 2000 Plus
        "B09N3QWCMF",  # EcoFlow DELTA 2
        "B0CQK8XCZQ",  # EcoFlow DELTA 2 Max
        "B0CGXKNWJX",  # Anker SOLIX C1000
    ],

    # 请求延迟范围 (秒)
    "min_delay": 3,
    "max_delay": 8,

    # 是否启用隐身模式
    "stealth_mode": True,
}

# 浏览器指纹池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 2560, "height": 1440},
]


@dataclass
class Product:
    """产品数据类"""
    brand: str
    name: str
    capacity: str
    current_price: float
    original_price: Optional[float]
    discount_percent: Optional[float]
    url: str
    last_updated: str
    currency: str = "CAD"
    source: str = "official"  # official / amazon


def load_config() -> Dict:
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置
            for key in DEFAULT_CONFIG:
                if key not in config:
                    config[key] = DEFAULT_CONFIG[key]
            return config
    else:
        # 创建默认配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()


def random_delay(config: Dict):
    """随机延迟"""
    delay = random.uniform(config["min_delay"], config["max_delay"])
    print(f"    等待 {delay:.1f} 秒...")
    time.sleep(delay)


def get_random_fingerprint() -> Dict:
    """获取随机浏览器指纹"""
    return {
        "user_agent": random.choice(USER_AGENTS),
        "viewport": random.choice(VIEWPORTS),
    }


def apply_stealth_scripts(page: Page):
    """
    注入隐身脚本，隐藏自动化特征
    模拟 playwright-stealth 的核心功能
    """
    stealth_js = """
    () => {
        // 1. 隐藏 webdriver 属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // 2. 伪装 plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' },
            ],
        });

        // 3. 伪装 languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-CA', 'en-US', 'en'],
        });

        // 4. 隐藏 automation 标志
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

        // 5. 伪装 permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // 6. 伪装 chrome runtime
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {},
        };

        // 7. 修复 iframe contentWindow
        const originalAttachShadow = Element.prototype.attachShadow;
        Element.prototype.attachShadow = function() {
            return originalAttachShadow.apply(this, arguments);
        };

        // 8. 伪装 WebGL vendor
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.apply(this, arguments);
        };

        // 9. 添加正常的屏幕属性
        Object.defineProperty(screen, 'availWidth', { get: () => screen.width });
        Object.defineProperty(screen, 'availHeight', { get: () => screen.height - 40 });

        // 10. 伪装 connection
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 100,
                downlink: 10,
                saveData: false,
            }),
        });
    }
    """
    page.add_init_script(stealth_js)


def simulate_human_behavior(page: Page):
    """模拟人类浏览行为"""
    try:
        # 随机滚动
        scroll_times = random.randint(2, 5)
        for _ in range(scroll_times):
            scroll_y = random.randint(100, 500)
            page.mouse.wheel(0, scroll_y)
            time.sleep(random.uniform(0.3, 0.8))

        # 随机鼠标移动
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))

    except Exception:
        pass


def parse_price(price_str: str) -> Optional[float]:
    """解析价格"""
    if not price_str:
        return None
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_capacity(name: str) -> str:
    """提取容量"""
    patterns = [
        r'(\d+\.?\d*\s*kWh)',
        r'(\d+\.?\d*\s*Wh)',
        r'(\d{3,4})(?:\s|$|,)',
    ]
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            cap = match.group(1).replace(' ', '')
            if cap.isdigit():
                return f"{cap}Wh"
            return cap
    return "N/A"


class ScreenshotManager:
    """截图管理器"""

    def __init__(self):
        self.screenshots = []
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    def capture(self, page: Page, brand: str, source: str, product_name: str = None) -> Optional[str]:
        """
        捕获页面截图

        Args:
            page: Playwright页面对象
            brand: 品牌名称
            source: 来源 (official/amazon)
            product_name: 产品名称（可选）

        Returns:
            截图文件的相对路径
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H-%M-%S")

            # 生成文件名
            safe_brand = re.sub(r'[^a-zA-Z0-9]', '_', brand)
            safe_source = re.sub(r'[^a-zA-Z0-9]', '_', source)
            filename = f"{date_str}_{safe_brand}_{safe_source}_{time_str}.png"

            # 按日期创建子目录
            date_dir = os.path.join(SCREENSHOTS_DIR, date_str)
            os.makedirs(date_dir, exist_ok=True)

            # 截图路径
            screenshot_path = os.path.join(date_dir, filename)
            relative_path = f"data/screenshots/{date_str}/{filename}"

            # 捕获全页截图
            page.screenshot(path=screenshot_path, full_page=True)

            # 记录截图元数据
            self.screenshots.append({
                "date": date_str,
                "time": now.strftime("%H:%M:%S"),
                "brand": brand,
                "source": source,
                "product_name": product_name,
                "path": relative_path,
                "timestamp": now.isoformat()
            })

            print(f"    📷 截图已保存: {filename}")
            return relative_path

        except Exception as e:
            print(f"    ⚠ 截图失败: {e}")
            return None

    def save_metadata(self):
        """保存截图元数据到JSON文件"""
        # 加载现有数据
        existing = {"screenshots": []}
        if os.path.exists(SCREENSHOTS_FILE):
            try:
                with open(SCREENSHOTS_FILE, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                pass

        # 合并新截图
        existing["screenshots"].extend(self.screenshots)

        # 只保留最近30天的截图
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        existing["screenshots"] = [
            s for s in existing["screenshots"]
            if s.get("date", "") >= cutoff_date
        ]

        # 按时间排序
        existing["screenshots"].sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        existing["last_updated"] = datetime.now().isoformat()

        with open(SCREENSHOTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        print(f"  📷 截图元数据已保存 ({len(self.screenshots)} 张新截图)")


class StealthBrowser:
    """隐身浏览器管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.proxy_index = 0

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._create_browser()
        return self

    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _get_next_proxy(self) -> Optional[Dict]:
        """获取下一个代理"""
        proxies = self.config.get("proxies", [])
        if not proxies:
            return None

        proxy = proxies[self.proxy_index % len(proxies)]
        self.proxy_index += 1

        # 解析代理格式
        if "@" in proxy:
            # 带认证: http://user:pass@host:port
            return {"server": proxy}
        else:
            return {"server": proxy}

    def _create_browser(self):
        """创建浏览器实例"""
        fingerprint = get_random_fingerprint()

        launch_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--lang=en-CA',
        ]

        proxy = self._get_next_proxy()

        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=launch_args,
        )

        context_options = {
            "viewport": fingerprint["viewport"],
            "user_agent": fingerprint["user_agent"],
            "locale": "en-CA",
            "timezone_id": "America/Toronto",
            "geolocation": {"latitude": 43.6532, "longitude": -79.3832},  # Toronto
            "permissions": ["geolocation"],
        }

        if proxy:
            context_options["proxy"] = proxy
            print(f"  使用代理: {proxy['server'][:30]}...")

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()

        # 应用隐身脚本
        if self.config.get("stealth_mode", True):
            apply_stealth_scripts(self.page)

    def rotate_identity(self):
        """轮换身份（新指纹+新代理）"""
        if self.context:
            self.context.close()
        self._create_browser()
        print("  ✓ 已轮换浏览器身份")

    def get_page(self) -> Page:
        return self.page


class AmazonCanadaScraper:
    """Amazon加拿大站爬虫"""
    BASE_URL = "https://www.amazon.ca"

    def __init__(self, config: Dict, screenshot_manager: ScreenshotManager = None):
        self.config = config
        self.asins = config.get("amazon_asins", [])
        self.screenshot_manager = screenshot_manager

    def scrape(self, browser: StealthBrowser) -> List[Product]:
        products = []
        page = browser.get_page()

        # 步骤1: Cookie预热 - 访问首页建立session
        print("  🔧 预热Amazon session...")
        try:
            page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(random.uniform(3, 6))

            # 模拟真实浏览行为
            page.evaluate('''() => {
                // 滚动页面
                window.scrollTo(0, Math.random() * 500);
            }''')
            time.sleep(random.uniform(1, 2))

            # 访问搜索页面增加真实性
            page.goto(f"{self.BASE_URL}/s?k=portable+power+station", wait_until="domcontentloaded", timeout=30000)
            time.sleep(random.uniform(2, 4))
            simulate_human_behavior(page)

            print("  ✓ Session预热完成")
        except Exception as e:
            print(f"  ⚠ 预热失败: {e}")

        for i, asin in enumerate(self.asins):
            try:
                print(f"  [{i+1}/{len(self.asins)}] 抓取 ASIN: {asin}")

                # 方法1: 尝试通过搜索页面进入（更自然）
                product = None
                try:
                    # 先搜索ASIN
                    search_url = f"{self.BASE_URL}/s?k={asin}"
                    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(random.uniform(2, 4))

                    # 检查是否被拦截
                    if not self._check_blocked(page):
                        # 点击第一个搜索结果
                        try:
                            # 查找产品链接
                            product_link = page.query_selector(f'a[href*="/dp/{asin}"]')
                            if product_link:
                                product_url = product_link.get_attribute('href')
                                if not product_url.startswith('http'):
                                    product_url = self.BASE_URL + product_url

                                # 点击进入产品页
                                page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
                                time.sleep(random.uniform(3, 6))
                                simulate_human_behavior(page)

                                if not self._check_blocked(page):
                                    product = self._extract_product(page, asin, product_url)
                        except:
                            pass
                except Exception as e:
                    print(f"    ⚠ 搜索方式失败: {e}")

                # 方法2: 如果搜索失败，直接访问产品页（带Referer）
                if not product:
                    url = f"{self.BASE_URL}/dp/{asin}"

                    # 添加Referer使其看起来是从搜索页过来的
                    page.goto(url, wait_until="domcontentloaded", timeout=30000, referer=f"{self.BASE_URL}/s?k=portable+power+station")
                    time.sleep(random.uniform(4, 8))

                    # 更深度的人类行为模拟
                    simulate_human_behavior(page)

                    # 额外的真实行为：查看图片
                    try:
                        page.evaluate('''() => {
                            const images = document.querySelectorAll('img[data-a-image-name="landingImage"]');
                            if (images.length > 0) {
                                images[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                            }
                        }''')
                        time.sleep(random.uniform(1, 2))
                    except:
                        pass

                    # 检查是否被拦截
                    if self._check_blocked(page):
                        print(f"    ⚠ 检测到反爬页面，跳过此产品...")
                        # 等待更长时间再继续
                        time.sleep(random.uniform(15, 25))
                        continue

                    # 提取产品信息
                    product = self._extract_product(page, asin, url)

                if product:
                    products.append(product)
                    print(f"    ✓ {product.name[:40]}... ${product.current_price}")
                    # 截图Amazon产品页面
                    if self.screenshot_manager:
                        self.screenshot_manager.capture(
                            page, product.brand, "amazon", product.name[:50]
                        )
                else:
                    print(f"    ✗ 未能提取产品信息")

                # 每2个产品轮换一次身份（更频繁）
                if (i + 1) % 2 == 0 and i < len(self.asins) - 1:
                    print(f"  ✓ 轮换浏览器身份")
                    browser.rotate_identity()
                    page = browser.get_page()
                    # 重新预热session
                    try:
                        page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(random.uniform(2, 4))
                    except:
                        pass

            except Exception as e:
                print(f"    ✗ 抓取失败: {e}")
                continue

        return products

    def _check_blocked(self, page: Page) -> bool:
        """检查是否被反爬拦截"""
        try:
            # 检查常见的反爬页面特征
            content = page.content().lower()
            blocked_signs = [
                "enter the characters you see below",
                "sorry, we just need to make sure you're not a robot",
                "type the characters you see in this image",
                "api-services-support@amazon.com",
            ]
            return any(sign in content for sign in blocked_signs)
        except:
            return False

    def _extract_product(self, page: Page, asin: str, url: str) -> Optional[Product]:
        """提取产品信息"""
        try:
            # 产品名称
            name = None
            name_selectors = [
                '#productTitle',
                '#title',
                'h1.a-size-large',
            ]
            for selector in name_selectors:
                elem = page.query_selector(selector)
                if elem:
                    name = elem.inner_text().strip()
                    break

            if not name:
                return None

            # 当前价格
            current_price = None
            price_selectors = [
                '.a-price .a-offscreen',
                '#priceblock_ourprice',
                '#priceblock_dealprice',
                '#priceblock_saleprice',
                '.a-price-whole',
                '#corePrice_feature_div .a-price .a-offscreen',
                '#apex_offerDisplay_desktop .a-price .a-offscreen',
            ]
            for selector in price_selectors:
                elem = page.query_selector(selector)
                if elem:
                    price_text = elem.inner_text()
                    current_price = parse_price(price_text)
                    if current_price:
                        break

            if not current_price:
                return None

            # 原价
            original_price = None
            original_selectors = [
                '.a-text-price .a-offscreen',
                '#listPrice',
                '.a-price[data-a-strike="true"] .a-offscreen',
            ]
            for selector in original_selectors:
                elem = page.query_selector(selector)
                if elem:
                    original_price = parse_price(elem.inner_text())
                    if original_price and original_price > current_price:
                        break
                    original_price = None

            # 判断品牌
            brand = "Amazon"
            name_lower = name.lower()
            if "jackery" in name_lower:
                brand = "Jackery"
            elif "ecoflow" in name_lower or "delta" in name_lower or "river" in name_lower:
                brand = "EcoFlow"
            elif "anker" in name_lower or "solix" in name_lower:
                brand = "Anker"

            # 计算折扣
            discount = None
            if original_price and original_price > current_price:
                discount = round((1 - current_price / original_price) * 100, 1)

            return Product(
                brand=brand,
                name=name,
                capacity=extract_capacity(name),
                current_price=current_price,
                original_price=original_price,
                discount_percent=discount,
                url=url,
                last_updated=datetime.now().isoformat(),
                source="amazon"
            )

        except Exception as e:
            print(f"    提取失败: {e}")
            return None


class OfficialSiteScraper:
    """官网爬虫（Jackery/EcoFlow/Anker）- 直接抓取产品页面"""

    def __init__(self, config: Dict, screenshot_manager: ScreenshotManager = None):
        self.config = config
        self.screenshot_manager = screenshot_manager

    def scrape(self, browser: StealthBrowser) -> List[Product]:
        products = []
        page = browser.get_page()

        # Jackery - 列表页
        try:
            jackery_products = self._scrape_jackery(page)
            products.extend(jackery_products)
        except Exception as e:
            print(f"    ✗ Jackery 列表页抓取失败: {e}")

        # 轮换身份
        browser.rotate_identity()
        page = browser.get_page()

        # Jackery - 抓取额外的产品页URL（列表页未能抓取的产品）
        jackery_urls = self.config.get("jackery_products", [])
        if jackery_urls:
            print(f"\n  抓取 Jackery 产品页 ({len(jackery_urls)} 个URL)...")
            for i, url in enumerate(jackery_urls):
                try:
                    product = self._scrape_product_page(page, url, "Jackery")
                    if product:
                        products.append(product)
                        print(f"    [{i+1}/{len(jackery_urls)}] ✓ {product.name} - ${product.current_price}")
                    else:
                        print(f"    [{i+1}/{len(jackery_urls)}] ✗ 无法提取: {url.split('/')[-1]}")
                    random_delay(self.config)
                except Exception as e:
                    print(f"    [{i+1}/{len(jackery_urls)}] ✗ 失败: {e}")

                # 每3个产品轮换身份
                if (i + 1) % 3 == 0 and i < len(jackery_urls) - 1:
                    browser.rotate_identity()
                    page = browser.get_page()

        # 轮换身份
        browser.rotate_identity()
        page = browser.get_page()

        # EcoFlow - 同时抓取产品页URL和列表页
        ecoflow_urls = self.config.get("ecoflow_products", [])
        if ecoflow_urls:
            print(f"\n  抓取 EcoFlow 产品页 ({len(ecoflow_urls)} 个URL)...")
            for i, url in enumerate(ecoflow_urls):
                try:
                    product = self._scrape_product_page(page, url, "EcoFlow")
                    if product:
                        products.append(product)
                        print(f"    [{i+1}/{len(ecoflow_urls)}] ✓ {product.name} - ${product.current_price}")
                    else:
                        print(f"    [{i+1}/{len(ecoflow_urls)}] ✗ 无法提取: {url.split('/')[-1]}")
                    random_delay(self.config)
                except Exception as e:
                    print(f"    [{i+1}/{len(ecoflow_urls)}] ✗ 失败: {e}")

                # 每3个产品轮换身份
                if (i + 1) % 3 == 0 and i < len(ecoflow_urls) - 1:
                    browser.rotate_identity()
                    page = browser.get_page()

        # 另外再抓取列表页以获取更多产品
        browser.rotate_identity()
        page = browser.get_page()
        try:
            print(f"\n  抓取 EcoFlow 列表页...")
            ecoflow_listing_products = self._scrape_ecoflow_listing(page)
            products.extend(ecoflow_listing_products)
            print(f"    ✓ 列表页提取 {len(ecoflow_listing_products)} 个产品")
        except Exception as e:
            print(f"    ✗ EcoFlow 列表页抓取失败: {e}")

        # 轮换身份
        browser.rotate_identity()
        page = browser.get_page()

        # Anker - 使用直接产品页面URL
        anker_urls = self.config.get("anker_products", [])
        if anker_urls:
            print(f"\n  抓取 Anker 官网 ({len(anker_urls)} 个产品)...")
            for i, url in enumerate(anker_urls):
                try:
                    product = self._scrape_product_page(page, url, "Anker")
                    if product:
                        products.append(product)
                        print(f"    [{i+1}/{len(anker_urls)}] ✓ {product.name} - ${product.current_price}")
                    else:
                        print(f"    [{i+1}/{len(anker_urls)}] ✗ 无法提取: {url.split('/')[-1]}")
                    random_delay(self.config)
                except Exception as e:
                    print(f"    [{i+1}/{len(anker_urls)}] ✗ 失败: {e}")

                # 每3个产品轮换身份
                if (i + 1) % 3 == 0 and i < len(anker_urls) - 1:
                    browser.rotate_identity()
                    page = browser.get_page()
        else:
            # 回退到列表页抓取
            try:
                anker_products = self._scrape_anker_listing(page)
                products.extend(anker_products)
            except Exception as e:
                print(f"    ✗ Anker 列表页抓取失败: {e}")

        return products

    def _scrape_product_page(self, page: Page, url: str, brand: str) -> Optional[Product]:
        """直接抓取单个产品页面"""
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)  # 等待JavaScript渲染

        # 检测404页面
        page_content = page.content()
        if "404" in page.title() or "not found" in page.title().lower() or "oops" in page.title().lower():
            print(f"    ✗ 页面不存在 (404): {url}")
            return None

        # 模拟人类行为
        simulate_human_behavior(page)

        # 截图
        if self.screenshot_manager:
            self.screenshot_manager.capture(page, brand, "official")

        # 使用品牌特定的产品页面提取逻辑
        product_data = page.evaluate('''(brand) => {
            const result = { name: null, current_price: null, original_price: null, capacity: null };

            // 1. 提取产品名称 - 尝试多种选择器
            const titleSelectors = [
                'h1.product__title',  // Shopify标准
                'h1[class*="title"]',
                'h1[class*="Title"]',
                '[class*="ProductTitle"]',
                'h1',
                '.product__title',
                '#product-title',
                '[data-testid="product-title"]',
                'meta[property="og:title"]'
            ];

            for (const sel of titleSelectors) {
                let el = null;
                if (sel.startsWith('meta')) {
                    el = document.querySelector(sel);
                    if (el) {
                        result.name = el.getAttribute('content');
                        break;
                    }
                } else {
                    el = document.querySelector(sel);
                    if (el && el.innerText && el.innerText.trim().length > 3) {
                        result.name = el.innerText.trim();
                        break;
                    }
                }
            }

            // 2. 提取容量信息 - 优先从产品名称提取，然后从页面其他位置查找
            // 先从产品名称提取（格式如: "3,072Wh" 或 "2048Wh" 或 "3.8kWh"）
            if (result.name) {
                const nameMatch = result.name.match(/([\\d,]+\\.?\\d*\\s*k?Wh)/i);
                if (nameMatch) {
                    result.capacity = nameMatch[1].replace(/\\s+/g, '').replace(/,/g, '');
                }
            }

            // 如果名称中没找到，再从页面其他位置查找
            if (!result.capacity) {
                const capacitySelectors = [
                    '[class*="capacity"]',
                    '[class*="Capacity"]',
                    '[class*="spec"]',
                    '[class*="Spec"]',
                    '.product__description',
                    '.product-description',
                    '[class*="detail"]'
                ];

                for (const sel of capacitySelectors) {
                    const els = document.querySelectorAll(sel);
                    els.forEach(el => {
                        if (result.capacity) return;
                        const text = el.innerText || el.textContent || '';
                        // 匹配容量格式: 2048Wh, 2,048Wh, 2.048kWh, 2000 Wh等
                        const match = text.match(/([\\d,]+\\.?\\d*\\s*k?Wh)/i);
                        if (match) {
                            result.capacity = match[1].replace(/\\s+/g, '').replace(/,/g, '');
                        }
                    });
                    if (result.capacity) break;
                }
            }

            // 3. 品牌特定的价格提取逻辑
            const prices = [];
            const skipPatterns = /off|save|discount|coupon|you save|was/i;

            if (brand === 'EcoFlow') {
                // EcoFlow 特定选择器 - 优先级策略
                const skipClassPatterns = /ecocredits|affirm|installment|off[^i]|save[^p]|discount|coupon|you save|was/i;

                // 优先1: 查找 Shopify 标准销售价格类
                const salePriceEls = document.querySelectorAll('.price-item--sale, .product-sticky-price');
                salePriceEls.forEach(el => {
                    const text = el.innerText || el.textContent || '';
                    const matches = text.match(/C?\\$([\\d,]+(?:\\.\\d{2})?)/g);
                    if (matches) {
                        matches.forEach(match => {
                            const price = parseFloat(match.replace(/[C$,]/g, ''));
                            if (price >= 100 && price < 20000) {
                                prices.push({ price, element: el.className, priority: 1 });
                            }
                        });
                    }
                });

                // 优先2: 如果没找到标准价格，查找其他价格元素（但排除 EcoCredits、分期付款等）
                if (prices.length === 0) {
                    const priceContainers = document.querySelectorAll('[class*="price"], .money, [data-price]');
                    priceContainers.forEach(el => {
                        // 跳过 EcoCredits、分期付款、折扣金额等
                        if (skipClassPatterns.test(el.className)) return;

                        const text = el.innerText || el.textContent || '';
                        if (skipPatterns.test(text)) return;

                        const matches = text.match(/C?\\$([\\d,]+(?:\\.\\d{2})?)/g);
                        if (matches) {
                            matches.forEach(match => {
                                const price = parseFloat(match.replace(/[C$,]/g, ''));
                                if (price >= 100 && price < 20000) {
                                    prices.push({ price, element: el.className, priority: 2 });
                                }
                            });
                        }
                    });
                }
            } else if (brand === 'Anker') {
                // 检测 Sold Out 状态
                const pageText = document.body.innerText.toLowerCase();
                if (pageText.includes('sold out') || pageText.includes('out of stock')) {
                    // 产品售罄，不返回价格
                    return result;
                }

                // Anker 特定选择器 - 优先查找特定的价格类
                const skipClassPatterns = /save|swiper.*discount|discount.*swiper/i;  // 跳过折扣金额和轮播图价格

                // 优先1: 查找实际销售价 - ProductTag_codePrice (折后价)
                const codePriceEls = document.querySelectorAll('[class*="ProductTag_codePrice"]');
                codePriceEls.forEach(el => {
                    const text = el.innerText || el.textContent || '';
                    const matches = text.match(/C?\\$([\\d,]+(?:\\.\\d{2})?)/g);
                    if (matches) {
                        matches.forEach(match => {
                            const price = parseFloat(match.replace(/[C$,]/g, ''));
                            if (price >= 100 && price < 20000) {
                                prices.push({ price, element: el.className, priority: 1 });
                            }
                        });
                    }
                });

                // 优先2: 如果没找到codePrice，查找salePrice（但排除savePrice和Swiper）
                if (prices.length === 0) {
                    const salePriceEls = document.querySelectorAll('.salePrice, [class*="salePrice"]');
                    salePriceEls.forEach(el => {
                        // 排除savePrice（折扣金额）和Swiper（轮播图）
                        if (/savePrice|swiper/i.test(el.className)) return;

                        const text = el.innerText || el.textContent || '';
                        const matches = text.match(/C?\\$([\\d,]+(?:\\.\\d{2})?)/g);
                        if (matches) {
                            matches.forEach(match => {
                                const price = parseFloat(match.replace(/[C$,]/g, ''));
                                if (price >= 100 && price < 20000) {
                                    prices.push({ price, element: el.className, priority: 2 });
                                }
                            });
                        }
                    });
                }

                // 优先3: 如果还没找到，查找所有价格元素（但跳过save/swiper/discount）
                if (prices.length === 0) {
                    const priceEls = document.querySelectorAll('[class*="price"], [class*="Price"], [data-testid*="price"], .money');
                    priceEls.forEach(el => {
                        // 跳过折扣金额和轮播图价格
                        if (skipClassPatterns.test(el.className)) return;

                        const text = el.innerText || el.textContent || '';
                        // 跳过明显是折扣信息的文本
                        if (/^save|^off|^discount|^you save/i.test(text.trim())) return;

                        const matches = text.match(/C?\\$([\\d,]+(?:\\.\\d{2})?)/g);
                        if (matches) {
                            matches.forEach(match => {
                                const price = parseFloat(match.replace(/[C$,]/g, ''));
                                if (price >= 100 && price < 20000) {
                                    prices.push({ price, element: el.className, priority: 2 });
                                }
                            });
                        }
                    });
                }
            } else {
                // 通用价格提取
                const priceSelectors = ['[class*="price"]', '[class*="Price"]', '.money', '[data-price]'];
                priceSelectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        const text = el.innerText || el.textContent || '';
                        if (skipPatterns.test(el.className) || skipPatterns.test(text)) return;

                        const matches = text.match(/C?\\$([\\d,]+(?:\\.\\d{2})?)/g);
                        if (matches) {
                            matches.forEach(match => {
                                const price = parseFloat(match.replace(/[C$,]/g, ''));
                                if (price >= 100 && price < 20000) {
                                    prices.push({ price, element: el.className });
                                }
                            });
                        }
                    });
                });
            }

            // 去重价格
            const uniquePrices = [...new Set(prices.map(p => p.price))].sort((a, b) => a - b);

            if (uniquePrices.length > 0) {
                result.current_price = uniquePrices[0];
                // 只有当有明确的原价标识时才设置原价
                if (uniquePrices.length > 1 && uniquePrices[uniquePrices.length - 1] > uniquePrices[0] * 1.1) {
                    result.original_price = uniquePrices[uniquePrices.length - 1];
                }
            }

            return result;
        }''', brand)

        if not product_data.get('name') or not product_data.get('current_price'):
            print(f"    ✗ 无法提取产品信息: {url}")
            print(f"      - Name: {product_data.get('name')}")
            print(f"      - Price: {product_data.get('current_price')}")
            return None

        # 提取容量：优先使用页面提取的容量，其次从产品名称提取
        capacity = product_data.get('capacity') or extract_capacity(product_data['name'])

        # 计算折扣
        discount = None
        if product_data.get('original_price') and product_data['original_price'] > product_data['current_price']:
            discount = round((1 - product_data['current_price'] / product_data['original_price']) * 100, 1)

        return Product(
            brand=brand,
            name=product_data['name'],
            capacity=capacity,
            current_price=product_data['current_price'],
            original_price=product_data.get('original_price'),
            discount_percent=discount,
            url=url,
            last_updated=datetime.now().isoformat(),
            source="official"
        )

    def _scrape_jackery(self, page: Page) -> List[Product]:
        """抓取 Jackery Canada"""
        print(f"\n  抓取 Jackery 官网...")
        products = []

        try:
            # 改用domcontentloaded，增加超时时间
            page.goto("https://www.jackery.ca/collections/portable-power-stations", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)  # 等待JavaScript渲染

            # 滚动加载所有产品
            for i in range(8):
                page.evaluate('window.scrollBy(0, 800)')
                time.sleep(1)

            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)

            page.evaluate('window.scrollTo(0, 0)')
            time.sleep(1)

            # 截图
            if self.screenshot_manager:
                self.screenshot_manager.capture(page, "Jackery", "official")
        except Exception as e:
            print(f"    ✗ 访问Jackery列表页失败: {e}")
            return []

        # 使用JavaScript直接提取产品数据
        product_data = page.evaluate('''() => {
            const products = [];
            const cards = document.querySelectorAll('.product-card, .product-item, [class*="product"]');

            cards.forEach(card => {
                try {
                    const link = card.querySelector('a[href*="/products/"]');
                    if (!link) return;

                    const url = link.href;
                    const titleEl = card.querySelector('.product-card__title, .product-title, h2, h3, [class*="title"]');
                    const title = titleEl ? titleEl.innerText.trim() : '';

                    if (!title.toLowerCase().includes('explorer') && !title.toLowerCase().includes('jackery')) return;

                    // 获取所有价格文本
                    const priceEls = card.querySelectorAll('[class*="price"], .money, span:not([class*="off"])');
                    const prices = [];
                    priceEls.forEach(el => {
                        const text = el.innerText;
                        if (text.includes('$') && !text.toLowerCase().includes('off') && !text.toLowerCase().includes('save')) {
                            const match = text.match(/\\$([\\d,]+\\.?\\d*)/);
                            if (match) {
                                const price = parseFloat(match[1].replace(',', ''));
                                if (price > 100) prices.push(price);
                            }
                        }
                    });

                    if (title && prices.length > 0) {
                        prices.sort((a, b) => a - b);
                        products.push({
                            name: title,
                            url: url,
                            current_price: prices[0],
                            original_price: prices.length > 1 ? prices[prices.length - 1] : null
                        });
                    }
                } catch (e) {}
            });
            return products;
        }''')

        for p in product_data:
            discount = None
            if p.get('original_price') and p['original_price'] > p['current_price']:
                discount = round((1 - p['current_price'] / p['original_price']) * 100, 1)

            products.append(Product(
                brand="Jackery",
                name=p['name'],
                capacity=extract_capacity(p['name']),
                current_price=p['current_price'],
                original_price=p.get('original_price'),
                discount_percent=discount,
                url=p['url'],
                last_updated=datetime.now().isoformat(),
                source="official"
            ))

        print(f"    ✓ Jackery 提取 {len(products)} 个产品")
        return products

    def _scrape_ecoflow_listing(self, page: Page) -> List[Product]:
        """抓取 EcoFlow Canada 列表页（备用方法）"""
        print(f"\n  抓取 EcoFlow 官网...")
        products = []

        try:
            # 改用domcontentloaded而不是networkidle，更快更可靠
            page.goto("https://ca.ecoflow.com/collections/portable-power-stations", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)  # 额外等待JavaScript渲染

            # 更积极的滚动加载策略
            for i in range(8):
                page.evaluate('window.scrollBy(0, 800)')
                time.sleep(1.2)

            # 滚动到底部
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)

            # 再滚回顶部（模拟真实用户行为）
            page.evaluate('window.scrollTo(0, 0)')
            time.sleep(1)

            # 截图
            if self.screenshot_manager:
                self.screenshot_manager.capture(page, "EcoFlow", "official")
        except Exception as e:
            print(f"    ✗ 访问EcoFlow列表页失败: {e}")
            return []

        # 使用JavaScript直接提取产品数据
        product_data = page.evaluate('''() => {
            const products = [];
            // EcoFlow 可能使用不同的产品卡片选择器
            const cards = document.querySelectorAll('[class*="product"], [class*="card"], .collection-product, article');

            cards.forEach(card => {
                try {
                    const link = card.querySelector('a[href*="/products/"], a[href*="/p/"], a[href*="delta"], a[href*="river"]');
                    if (!link) return;

                    const url = link.href.startsWith('http') ? link.href : 'https://ca.ecoflow.com' + link.getAttribute('href');

                    // 查找标题
                    const titleEl = card.querySelector('h2, h3, h4, [class*="title"], [class*="name"]');
                    let title = titleEl ? titleEl.innerText.trim() : '';

                    // 检查是否是PPS产品
                    const cardText = card.innerText.toLowerCase();
                    if (!cardText.includes('delta') && !cardText.includes('river')) return;

                    if (!title || title.length < 3) {
                        // 尝试从链接文本获取
                        title = link.innerText.trim() || link.getAttribute('title') || '';
                    }

                    // 获取价格
                    const allText = card.innerText;
                    const priceMatches = allText.match(/\\$([\\d,]+\\.?\\d*)/g) || [];
                    const prices = [];

                    priceMatches.forEach(match => {
                        const price = parseFloat(match.replace('$', '').replace(',', ''));
                        // 过滤掉太小的数字（折扣金额）和OFF相关的
                        if (price > 200) {
                            prices.push(price);
                        }
                    });

                    if (prices.length > 0) {
                        prices.sort((a, b) => a - b);
                        const uniquePrices = [...new Set(prices)];

                        // 从URL或卡片文本推断产品名
                        if (!title || title.length < 5) {
                            if (cardText.includes('delta pro')) title = 'DELTA Pro';
                            else if (cardText.includes('delta 2 max')) title = 'DELTA 2 Max';
                            else if (cardText.includes('delta 2')) title = 'DELTA 2';
                            else if (cardText.includes('river 2 pro')) title = 'RIVER 2 Pro';
                            else if (cardText.includes('river 2 max')) title = 'RIVER 2 Max';
                            else if (cardText.includes('river 2')) title = 'RIVER 2';
                        }

                        if (title) {
                            products.push({
                                name: title,
                                url: url,
                                current_price: uniquePrices[0],
                                original_price: uniquePrices.length > 1 ? uniquePrices[uniquePrices.length - 1] : null
                            });
                        }
                    }
                } catch (e) {}
            });

            // 去重
            const seen = new Set();
            return products.filter(p => {
                const key = p.name + p.current_price;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });
        }''')

        for p in product_data:
            discount = None
            if p.get('original_price') and p['original_price'] > p['current_price']:
                discount = round((1 - p['current_price'] / p['original_price']) * 100, 1)

            products.append(Product(
                brand="EcoFlow",
                name=p['name'],
                capacity=extract_capacity(p['name']),
                current_price=p['current_price'],
                original_price=p.get('original_price'),
                discount_percent=discount,
                url=p['url'],
                last_updated=datetime.now().isoformat(),
                source="official"
            ))

        print(f"    ✓ EcoFlow 提取 {len(products)} 个产品")
        return products

    def _scrape_anker_listing(self, page: Page) -> List[Product]:
        """抓取 Anker Canada 列表页（备用方法）"""
        print(f"\n  抓取 Anker 官网...")
        products = []

        try:
            # 改用domcontentloaded，增加超时时间
            page.goto("https://www.anker.com/ca/collections/portable-power-stations", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)  # 等待JavaScript渲染

            # 更积极的滚动加载
            for i in range(10):
                page.evaluate('window.scrollBy(0, 800)')
                time.sleep(1)

            # 滚动到底部
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(3)

            # 滚回顶部
            page.evaluate('window.scrollTo(0, 0)')
            time.sleep(1)

            # 截图
            if self.screenshot_manager:
                self.screenshot_manager.capture(page, "Anker", "official")
        except Exception as e:
            print(f"    ✗ 访问Anker列表页失败: {e}")
            return []

        # 使用JavaScript直接提取产品数据
        product_data = page.evaluate('''() => {
            const products = [];
            const cards = document.querySelectorAll('[class*="product"], [class*="card"], article, .grid-item');

            cards.forEach(card => {
                try {
                    const link = card.querySelector('a[href*="/products/"], a[href*="solix"], a[href*="power-station"]');
                    if (!link) return;

                    let url = link.href;
                    if (!url.startsWith('http')) {
                        url = 'https://www.anker.com' + link.getAttribute('href');
                    }

                    // 查找标题
                    const titleEl = card.querySelector('h2, h3, h4, [class*="title"], [class*="name"], .product-name');
                    let title = titleEl ? titleEl.innerText.trim() : '';

                    // 检查是否是SOLIX产品
                    const cardText = card.innerText.toLowerCase();
                    if (!cardText.includes('solix') && !cardText.includes('power station') && !cardText.includes('powerhouse')) return;

                    // 获取价格 - 查找所有包含$的文本
                    const allText = card.innerText;
                    const priceMatches = allText.match(/C?\\$([\\d,]+\\.?\\d*)/g) || [];
                    const prices = [];

                    priceMatches.forEach(match => {
                        const price = parseFloat(match.replace(/[C$,]/g, ''));
                        // 过滤掉太小的数字（折扣金额如$1,500 OFF）
                        if (price > 200 && !allText.toLowerCase().includes(price + ' off')) {
                            prices.push(price);
                        }
                    });

                    if (prices.length > 0 && title) {
                        prices.sort((a, b) => a - b);
                        const uniquePrices = [...new Set(prices)];

                        products.push({
                            name: title,
                            url: url,
                            current_price: uniquePrices[0],
                            original_price: uniquePrices.length > 1 ? uniquePrices[uniquePrices.length - 1] : null
                        });
                    }
                } catch (e) {}
            });

            // 去重
            const seen = new Set();
            return products.filter(p => {
                const key = p.name + p.current_price;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });
        }''')

        for p in product_data:
            discount = None
            if p.get('original_price') and p['original_price'] > p['current_price']:
                discount = round((1 - p['current_price'] / p['original_price']) * 100, 1)

            products.append(Product(
                brand="Anker",
                name=p['name'],
                capacity=extract_capacity(p['name']),
                current_price=p['current_price'],
                original_price=p.get('original_price'),
                discount_percent=discount,
                url=p['url'],
                last_updated=datetime.now().isoformat(),
                source="official"
            ))

        print(f"    ✓ Anker 提取 {len(products)} 个产品")
        return products


def save_data(products: List[Product]):
    """保存数据"""
    # 保存当前价格
    data = {
        "last_updated": datetime.now().isoformat(),
        "products": [asdict(p) for p in products]
    }
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 更新历史
    history = {"records": []}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    daily_record = {
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "prices": {}
    }

    for p in products:
        key = f"{p.brand}|{p.name}"
        daily_record["prices"][key] = {
            "current_price": p.current_price,
            "original_price": p.original_price,
            "discount_percent": p.discount_percent,
            "source": p.source
        }

    # 更新或添加今日记录
    found = False
    for i, record in enumerate(history["records"]):
        if record["date"] == today:
            history["records"][i] = daily_record
            found = True
            break
    if not found:
        history["records"].append(daily_record)

    history["records"] = history["records"][-30:]

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def run_stealth_scraper():
    """运行隐身爬虫"""
    print("=" * 60)
    print("PPS价格监控 - 增强版 (反反爬虫)")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    os.makedirs(DATA_DIR, exist_ok=True)
    config = load_config()

    all_products = []

    # 创建截图管理器
    screenshot_manager = ScreenshotManager()

    with StealthBrowser(config) as browser:
        # 1. 抓取官网
        print("\n[阶段1] 抓取品牌官网...")
        official_scraper = OfficialSiteScraper(config, screenshot_manager)
        official_products = official_scraper.scrape(browser)
        all_products.extend(official_products)
        print(f"  官网共获取 {len(official_products)} 个产品")

        # 轮换身份
        browser.rotate_identity()

        # 2. 抓取Amazon
        if config.get("amazon_asins"):
            print("\n[阶段2] 抓取 Amazon Canada...")
            amazon_scraper = AmazonCanadaScraper(config, screenshot_manager)
            amazon_products = amazon_scraper.scrape(browser)
            all_products.extend(amazon_products)
            print(f"  Amazon共获取 {len(amazon_products)} 个产品")

    # 保存数据
    if all_products:
        save_data(all_products)
        print(f"\n{'=' * 60}")
        print(f"✓ 总计抓取 {len(all_products)} 个产品")
        print(f"  - 官网: {len([p for p in all_products if p.source == 'official'])}")
        print(f"  - Amazon: {len([p for p in all_products if p.source == 'amazon'])}")
        print(f"数据已保存")
    else:
        print("\n⚠ 未抓取到任何产品")

    # 保存截图元数据
    screenshot_manager.save_metadata()

    print("=" * 60)
    return all_products


if __name__ == "__main__":
    run_stealth_scraper()
