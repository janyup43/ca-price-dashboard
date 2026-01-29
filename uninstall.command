#!/bin/bash
# 卸载 PPS 价格监控定时任务
echo "======================================"
echo "  PPS 价格监控 - 卸载定时任务"
echo "======================================"
echo ""

PLIST_FILE="$HOME/Library/LaunchAgents/com.pps.pricemonitor.plist"

if [ -f "$PLIST_FILE" ]; then
    launchctl unload "$PLIST_FILE" 2>/dev/null
    rm "$PLIST_FILE"
    echo "✓ 已移除每日自动运行任务"
else
    echo "⚠ 未找到定时任务配置"
fi

echo ""
echo "注意: 项目文件未删除，如需完全删除请手动删除项目文件夹"
echo ""
read -p "按任意键退出..."
