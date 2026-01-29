#!/bin/bash

# CA价格看板 - 隧道管理脚本

case "$1" in
    start)
        echo "🚀 启动 Localtunnel 保活服务..."
        if pgrep -f "keep_tunnel_alive.sh" > /dev/null; then
            echo "⚠️  服务已在运行"
            exit 0
        fi
        nohup bash ~/Downloads/ca-price-dashboard/keep_tunnel_alive.sh > /dev/null 2>&1 &
        sleep 3
        if pgrep -f "keep_tunnel_alive.sh" > /dev/null; then
            echo "✅ 服务启动成功"
            tail -5 ~/Downloads/ca-price-dashboard/tunnel.log
        else
            echo "❌ 服务启动失败"
            exit 1
        fi
        ;;
    
    stop)
        echo "🛑 停止 Localtunnel 服务..."
        pkill -f "keep_tunnel_alive.sh"
        pkill -f "lt --port 8080"
        sleep 1
        echo "✅ 服务已停止"
        ;;
    
    restart)
        echo "🔄 重启 Localtunnel 服务..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo "📊 Localtunnel 服务状态"
        echo "================================"
        if pgrep -f "keep_tunnel_alive.sh" > /dev/null; then
            echo "保活脚本: ✅ 运行中 (PID: $(pgrep -f 'keep_tunnel_alive.sh' | head -1))"
        else
            echo "保活脚本: ❌ 未运行"
        fi
        
        if pgrep -f "lt --port 8080" > /dev/null; then
            echo "Localtunnel: ✅ 运行中 (PID: $(pgrep -f 'lt --port 8080'))"
            echo ""
            echo "🌐 公网地址: https://stupid-times-call.loca.lt/index.html"
        else
            echo "Localtunnel: ❌ 未运行"
        fi
        
        echo ""
        echo "📝 最近日志:"
        tail -5 ~/Downloads/ca-price-dashboard/tunnel.log
        ;;
    
    log)
        echo "📜 实时日志 (Ctrl+C 退出):"
        tail -f ~/Downloads/ca-price-dashboard/tunnel.log
        ;;
    
    *)
        echo "CA价格看板 - Localtunnel 管理工具"
        echo ""
        echo "用法: $0 {start|stop|restart|status|log}"
        echo ""
        echo "命令:"
        echo "  start   - 启动隧道服务"
        echo "  stop    - 停止隧道服务"
        echo "  restart - 重启隧道服务"
        echo "  status  - 查看服务状态"
        echo "  log     - 查看实时日志"
        exit 1
        ;;
esac
