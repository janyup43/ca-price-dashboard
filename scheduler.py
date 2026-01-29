#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时任务调度器
在配置的时间范围内随机选择一个时间点运行爬虫
"""

import json
import os
import random
import time
from datetime import datetime, timedelta
import subprocess
import sys

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'data', 'config.json')
SCRAPER_FILE = os.path.join(os.path.dirname(__file__), 'scraper_stealth.py')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'data', 'scheduler.log')


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')


def load_config() -> dict:
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_next_run_time(config: dict) -> datetime:
    """计算下次运行时间"""
    daily_config = config.get('daily_run', {})
    hour_range = daily_config.get('random_hour_range', [6, 10])

    now = datetime.now()

    # 在时间范围内随机选择
    random_hour = random.randint(hour_range[0], hour_range[1])
    random_minute = random.randint(0, 59)

    # 构建今天的运行时间
    run_time = now.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

    # 如果已经过了今天的时间，安排到明天
    if run_time <= now:
        run_time += timedelta(days=1)

    return run_time


def run_scraper():
    """运行爬虫"""
    log("开始运行爬虫...")
    try:
        result = subprocess.run(
            [sys.executable, SCRAPER_FILE],
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        if result.returncode == 0:
            log("爬虫运行成功")
            # 记录部分输出
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-5:]:  # 最后5行
                log(f"  {line}")
        else:
            log(f"爬虫运行失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        log("爬虫运行超时")
    except Exception as e:
        log(f"运行错误: {e}")


def main():
    """主调度循环"""
    log("=" * 50)
    log("PPS价格监控 - 每日调度器启动")
    log("=" * 50)

    config = load_config()
    daily_config = config.get('daily_run', {})

    if not daily_config.get('enabled', True):
        log("每日任务已禁用，退出")
        return

    while True:
        try:
            # 计算下次运行时间
            next_run = get_next_run_time(config)
            wait_seconds = (next_run - datetime.now()).total_seconds()

            log(f"下次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            log(f"等待 {wait_seconds/3600:.1f} 小时")

            # 等待到运行时间
            if wait_seconds > 0:
                time.sleep(wait_seconds)

            # 运行爬虫
            run_scraper()

            # 添加随机延迟避免精确模式
            jitter = random.randint(60, 300)  # 1-5分钟随机延迟
            log(f"添加 {jitter} 秒随机延迟后继续...")
            time.sleep(jitter)

        except KeyboardInterrupt:
            log("收到中断信号，退出调度器")
            break
        except Exception as e:
            log(f"调度器错误: {e}")
            time.sleep(60)  # 出错后等待1分钟重试


if __name__ == "__main__":
    main()
