# 🌐 CA价格看板 - 稳定公网访问配置

## ✅ 配置完成

你的 PPS 价格监控系统现在已配置为**自动保活**的公网访问方式！

---

## 🌟 功能特性

### 1. **自动重连**
- 当 localtunnel 断开时，会在 5 秒内自动重启
- 无需手动干预，保持连接稳定

### 2. **开机自启动**
- 系统重启后自动启动隧道服务
- 通过 macOS launchd 实现

### 3. **完整日志**
- 所有连接状态和错误都会记录到日志文件
- 方便问题排查

---

## 📱 访问地址

**公网地址**: https://stupid-times-call.loca.lt/index.html  
**本地地址**: http://localhost:8080/index.html

---

## 🎮 管理方式

### 方式 1: 桌面快捷方式（推荐）
双击桌面上的 **"PPS隧道管理.command"** 文件，可以：
- ✅ 启动/停止/重启隧道
- ✅ 查看运行状态
- ✅ 查看实时日志

### 方式 2: 命令行
```bash
cd ~/Downloads/ca-price-dashboard

# 启动隧道
./manage_tunnel.sh start

# 停止隧道
./manage_tunnel.sh stop

# 重启隧道
./manage_tunnel.sh restart

# 查看状态
./manage_tunnel.sh status

# 查看实时日志
./manage_tunnel.sh log
```

---

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `keep_tunnel_alive.sh` | 保活脚本，自动重启断开的隧道 |
| `manage_tunnel.sh` | 管理脚本，提供启动/停止/状态查询 |
| `tunnel.log` | 隧道运行日志 |
| `launchd_stdout.log` | Launchd 标准输出日志 |
| `launchd_stderr.log` | Launchd 错误日志 |

---

## 🔧 故障排除

### 问题 1: 隧道无法启动
**解决方法**:
```bash
# 检查端口是否被占用
lsof -i :8080

# 检查 node 和 lt 是否安装
which node
which lt

# 查看错误日志
cat ~/Downloads/ca-price-dashboard/launchd_stderr.log
```

### 问题 2: 子域名被占用
如果 `stupid-times-call` 被其他人占用，修改子域名：
```bash
# 编辑保活脚本
nano ~/Downloads/ca-price-dashboard/keep_tunnel_alive.sh

# 修改这一行:
SUBDOMAIN="your-new-subdomain"
```

### 问题 3: 开机自启动失败
```bash
# 卸载旧配置
launchctl unload ~/Library/LaunchAgents/com.pps.tunnel.plist

# 重新加载
launchctl load ~/Library/LaunchAgents/com.pps.tunnel.plist

# 查看状态
launchctl list | grep pps
```

---

## 🚀 升级建议

如需更稳定的解决方案，可以考虑：

### 选项 1: Cloudflare Tunnel (推荐)
- ✅ 完全免费
- ✅ 非常稳定
- ✅ 支持自定义域名
- ❌ 需要注册 Cloudflare 账号

安装方法:
```bash
brew install cloudflare/cloudflare/cloudflared
cloudflared tunnel login
cloudflared tunnel --url http://localhost:8080
```

### 选项 2: ngrok
- ✅ 更稳定
- ✅ 免费套餐可用
- ❌ 需要注册账号
- ❌ 免费版有会话时间限制

安装方法:
```bash
brew install ngrok
ngrok config add-authtoken <your-token>
ngrok http 8080
```

---

## 📞 联系支持

如有问题，请检查:
1. 服务状态: `./manage_tunnel.sh status`
2. 日志文件: `tunnel.log`
3. 本地访问: http://localhost:8080

---

**配置时间**: 2026-01-29  
**版本**: 1.0
