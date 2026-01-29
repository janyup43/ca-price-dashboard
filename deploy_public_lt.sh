#!/bin/bash
# 使用 localtunnel 创建公网访问（无需注册）

echo "正在安装 localtunnel..."
npm install -g localtunnel 2>/dev/null || {
    echo "需要先安装 Node.js 和 npm"
    echo "请访问: https://nodejs.org/"
    exit 1
}

echo ""
echo "=========================================="
echo "正在创建公网访问链接..."
echo "=========================================="
echo ""

# 启动 localtunnel
lt --port 8765 --print-requests
