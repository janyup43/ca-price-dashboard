#!/bin/bash
# PPS Price Monitor - Mac 一键安装脚本
# 双击此文件即可完成安装和配置

cd "$(dirname "$0")"
INSTALL_PATH="$(pwd)"

echo "======================================"
echo "  PPS 价格监控系统 - 安装程序"
echo "======================================"
echo ""
echo "安装路径: $INSTALL_PATH"
echo ""

# 1. 检查 Python
echo "[1/5] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python"
    echo "   下载地址: https://www.python.org/downloads/"
    read -p "按任意键退出..."
    exit 1
fi
echo "✓ Python3 已安装: $(python3 --version)"

# 2. 安装 Playwright
echo ""
echo "[2/5] 安装 Playwright..."
pip3 install playwright --quiet
if [ $? -ne 0 ]; then
    echo "❌ Playwright 安装失败"
    read -p "按任意键退出..."
    exit 1
fi
echo "✓ Playwright 已安装"

# 3. 安装 Chromium 浏览器
echo ""
echo "[3/5] 安装 Chromium 浏览器 (约200MB)..."
python3 -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "❌ Chromium 安装失败"
    read -p "按任意键退出..."
    exit 1
fi
echo "✓ Chromium 已安装"

# 4. 配置每日自动运行
echo ""
echo "[4/5] 配置每日自动运行 (每天早上8点)..."

# 创建 LaunchAgent 配置
PLIST_FILE="$HOME/Library/LaunchAgents/com.pps.pricemonitor.plist"
mkdir -p "$HOME/Library/LaunchAgents"

# 替换路径并复制配置文件
sed "s|__INSTALL_PATH__|$INSTALL_PATH|g" "$INSTALL_PATH/com.pps.pricemonitor.plist" > "$PLIST_FILE"

# 加载定时任务
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"

echo "✓ 已配置每日 8:00 自动运行"

# 5. 首次运行爬虫
echo ""
echo "[5/5] 首次运行爬虫获取数据..."
echo "======================================"
python3 scraper_stealth.py
echo "======================================"

# 完成
echo ""
echo "✅ 安装完成！"
echo ""
echo "📊 功能说明:"
echo "   - 每天早上 8:00 自动抓取价格"
echo "   - 数据保存在 $INSTALL_PATH/data/"
echo "   - 截图保存在 $INSTALL_PATH/data/screenshots/"
echo ""
echo "📂 常用操作:"
echo "   - 查看看板: 双击 view.command"
echo "   - 手动运行: 双击 run.command"
echo "   - 卸载定时: 双击 uninstall.command"
echo ""
read -p "按任意键启动看板..."

# 启动本地服务器
echo ""
echo "🌐 启动本地服务器..."
echo "   浏览器打开: http://localhost:8080"
echo "   按 Ctrl+C 停止服务器"
open "http://localhost:8080"
python3 -m http.server 8080
