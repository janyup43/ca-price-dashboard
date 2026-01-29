#!/usr/bin/env python3
"""
部署公开访问链接
使用 pyngrok 创建公网隧道
"""

import subprocess
import sys
import time

def install_pyngrok():
    """安装 pyngrok"""
    print("正在安装 pyngrok...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "-q"])
    print("✓ pyngrok 安装完成")

def create_public_url():
    """创建公网访问URL"""
    try:
        from pyngrok import ngrok
    except ImportError:
        install_pyngrok()
        from pyngrok import ngrok

    # 创建到本地服务器的隧道
    print("\n正在创建公网访问链接...")
    public_url = ngrok.connect(8765, bind_tls=True)

    print("\n" + "="*60)
    print("🎉 公网访问链接已创建！")
    print("="*60)
    print(f"\n公开链接: {public_url.public_url}")
    print(f"本地链接: http://localhost:8765/index.html")
    print("\n任何人都可以通过公开链接访问你的价格监控看板")
    print("\n提示：")
    print("  - 此链接在当前终端会话期间有效")
    print("  - 关闭此脚本后链接将失效")
    print("  - 按 Ctrl+C 可以停止公网访问")
    print("\n" + "="*60)

    # 保持运行
    try:
        print("\n保持运行中... (按 Ctrl+C 停止)\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n正在关闭公网访问...")
        ngrok.kill()
        print("✓ 已关闭")

if __name__ == '__main__':
    create_public_url()
