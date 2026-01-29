#!/bin/bash
# 查看 PPS 价格看板
cd "$(dirname "$0")"
echo "🌐 启动本地服务器..."
echo "   浏览器打开: http://localhost:8080"
echo "   按 Ctrl+C 停止服务器"
open "http://localhost:8080"
python3 -m http.server 8080
