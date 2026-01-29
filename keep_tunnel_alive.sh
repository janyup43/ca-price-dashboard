#!/bin/bash

# CA价格看板 - Localtunnel 保活脚本
# 功能：自动重启断开的 localtunnel 连接

LOG_FILE="$HOME/Downloads/ca-price-dashboard/tunnel.log"
PORT=8080
SUBDOMAIN="stupid-times-call"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=========================================="
log_message "Localtunnel 保活脚本启动"
log_message "端口: $PORT | 子域名: $SUBDOMAIN"
log_message "=========================================="

while true; do
    log_message "正在启动 localtunnel..."
    
    # 启动 localtunnel，捕获输出
    lt --port $PORT --subdomain $SUBDOMAIN 2>&1 | while IFS= read -r line; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line" >> "$LOG_FILE"
        # 如果输出包含 URL，显示到控制台
        if [[ "$line" == *"your url is:"* ]]; then
            log_message "✅ 隧道已建立: $line"
        fi
    done
    
    EXIT_CODE=$?
    log_message "⚠️  Localtunnel 断开 (退出码: $EXIT_CODE)"
    log_message "5秒后重启..."
    sleep 5
done
