# 📊 CA价格看板

加拿大便携式电源价格监控系统 - 实时追踪 EcoFlow、Jackery、Anker 三大品牌的官方价格

---

## 🌟 项目特点

### 监控品牌
- 🔵 **EcoFlow** (36个产品) - River/Delta/Trail 系列
- 🟠 **Jackery** (19个产品) - Explorer 系列
- 🟣 **Anker Solix** (40个产品) - C/F 系列

### 核心功能
- ✅ 实时价格监控（每日自动抓取）
- ✅ 历史价格趋势分析
- ✅ 折扣计算和最佳价格提示
- ✅ 品牌排序：EcoFlow → Jackery → Anker
- ✅ 价格排序：每个品牌内按价格从低到高
- ✅ 公网访问（通过 Localtunnel）
- ✅ 自动保活机制（断线自动重连）
- ✅ 开机自启动

---

## 🌐 访问方式

- **本地访问**: http://localhost:8080/index.html
- **公网访问**: https://stupid-times-call.loca.lt/index.html

---

## 🎮 管理工具

### 桌面快捷方式（推荐）
双击桌面的 **"CA价格看板管理.command"** 即可：
- 启动/停止/重启隧道服务
- 查看运行状态
- 查看实时日志

### 命令行操作
```bash
cd ~/Downloads/ca-price-dashboard

# 查看状态
./manage_tunnel.sh status

# 启动隧道
./manage_tunnel.sh start

# 停止隧道
./manage_tunnel.sh stop

# 重启隧道
./manage_tunnel.sh restart

# 查看日志
./manage_tunnel.sh log
```

---

## 📁 项目结构

```
ca-price-dashboard/
├── index.html                   # 主页面
├── data/                        # 数据目录
│   ├── prices.json             # 当前价格数据
│   ├── history.json            # 历史价格记录
│   ├── config.json             # 配置文件
│   └── screenshots/            # 页面截图
├── scraper_stealth.py          # 价格爬虫（反爬虫对抗）
├── keep_tunnel_alive.sh        # 隧道保活脚本
├── manage_tunnel.sh            # 隧道管理脚本
└── TUNNEL_SETUP.md             # 详细配置文档
```

---

## 🔄 自动任务

### 价格抓取
- **时间**: 每天 6:00-10:00 之间随机时间
- **内容**: 从官网抓取最新价格和折扣信息
- **日志**: `data/cron.log`

### 隧道保活
- **机制**: 检测到断开后 5 秒内自动重连
- **日志**: `tunnel.log`

---

## 🛠️ 技术栈

- **后端**: Python + Playwright（隐蔽模式爬虫）
- **前端**: HTML5 + CSS3 + Chart.js
- **数据**: JSON 文件存储
- **隧道**: Localtunnel（公网访问）
- **调度**: macOS launchd

---

## 📝 维护说明

### 手动运行价格抓取
```bash
cd ~/Downloads/ca-price-dashboard
python3 scraper_stealth.py
```

### 查看隧道日志
```bash
tail -f ~/Downloads/ca-price-dashboard/tunnel.log
```

### 重启所有服务
```bash
# 停止所有服务
pkill -f "http.server 8080"
./manage_tunnel.sh stop

# 启动服务
python3 -m http.server 8080 &
./manage_tunnel.sh start
```

---

## 📞 快速命令

```bash
# 项目别名：CA价格看板
cd ~/Downloads/ca-price-dashboard

# 查看最新价格
cat data/prices.json | python3 -m json.tool | less

# 查看历史记录
cat data/history.json | python3 -m json.tool | less

# 检查服务状态
ps aux | grep -E "(http.server 8080|lt --port 8080)"
```

---

**项目更新**: 2026-01-29  
**原名称**: PPS Price Monitor  
**新名称**: CA价格看板

---

## 🤖 自动化部署

### GitHub Actions 云端自动抓取

即使电脑关机，也能每天自动抓取价格！

- ⏰ **运行时间**: 加拿大东部时间每天 **00:00** (午夜)
- 🌐 **运行环境**: GitHub Actions (完全免费)
- 📊 **自动提交**: 数据自动更新到 GitHub 仓库
- 🚀 **手动触发**: 可随时在 GitHub 上手动运行

**详细设置步骤**: 查看 [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

### 快速部署

```bash
# 1. 在 GitHub 上创建仓库 ca-price-dashboard

# 2. 推送代码
cd ~/Downloads/ca-price-dashboard
git add .
git commit -m "🎉 Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ca-price-dashboard.git
git push -u origin main

# 3. 在 GitHub 仓库设置中启用 Actions 写入权限

# 4. 等待每天自动运行，或手动触发测试
```

---

## 📅 数据更新时间

- **本地定时任务**: 每天 6:00-10:00 随机时间（如果电脑开机）
- **GitHub Actions**: 每天 00:00 加拿大东部时间（电脑关机也运行）

两者可同时运行，数据会自动合并。

---
