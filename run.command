#!/bin/bash
cd "$(dirname "$0")"
echo "=============================="
echo "PPS 价格监控爬虫启动中..."
echo "=============================="
python3 scraper_stealth.py
echo ""
echo "=============================="
echo "爬虫运行完成！"
echo "按任意键启动本地服务器查看结果..."
read -n 1
echo "启动服务器: http://localhost:8080"
echo "在浏览器中打开此地址查看看板"
echo "按 Ctrl+C 停止服务器"
python3 -m http.server 8080
