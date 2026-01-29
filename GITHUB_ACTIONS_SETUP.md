# 🚀 GitHub Actions 自动价格抓取设置指南

## 📋 概述

通过 GitHub Actions，CA价格看板可以在**云端自动运行**，即使你的电脑关机也能：
- ✅ 每天在**加拿大东部时间 00:00**（午夜）自动抓取价格
- ✅ 自动提交更新后的数据到 GitHub
- ✅ 完全免费，无需服务器
- ✅ 可随时手动触发抓取

---

## 🎯 部署步骤

### 1. 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 `+` → `New repository`
3. 填写仓库信息：
   - **Repository name**: `ca-price-dashboard`
   - **Description**: `加拿大便携式电源价格监控系统`
   - **Privacy**: Private（推荐）或 Public
4. 点击 `Create repository`

### 2. 推送代码到 GitHub

在项目目录执行以下命令：

```bash
cd ~/Downloads/ca-price-dashboard

# 添加所有文件
git add .

# 第一次提交
git commit -m "🎉 Initial commit - CA Price Dashboard"

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/ca-price-dashboard.git

# 推送代码
git branch -M main
git push -u origin main
```

**注意**：如果推送失败，可能需要设置 GitHub 个人访问令牌：

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → 勾选 `repo` 权限
3. 复制生成的 token
4. 推送时使用：
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/ca-price-dashboard.git
   git push -u origin main
   ```

### 3. 配置 GitHub Actions 权限

1. 进入你的 GitHub 仓库
2. 点击 `Settings` → 左侧 `Actions` → `General`
3. 滚动到 **Workflow permissions** 部分
4. 选择 `Read and write permissions`
5. 勾选 `Allow GitHub Actions to create and approve pull requests`
6. 点击 `Save`

### 4. 验证自动化设置

1. 进入仓库的 `Actions` 标签页
2. 你应该能看到 `Daily Price Scraper` workflow
3. 点击右侧的 `Run workflow` 按钮手动测试
4. 等待几分钟，查看运行结果

---

## ⏰ 运行时间说明

### 自动运行
- **时间**: 加拿大东部时间（EST/EDT）每天 **00:00**（午夜）
- **对应 UTC**: 
  - 冬令时（11月-3月）: UTC 05:00
  - 夏令时（3月-11月）: UTC 04:00
- **GitHub Actions cron**: `0 5 * * *`（UTC 时间）

**注意**：GitHub Actions 的 cron 时间基于 UTC，可能有几分钟的延迟。

### 手动触发
随时可以在 GitHub Actions 页面手动运行：
1. 进入 `Actions` 标签
2. 选择 `Daily Price Scraper`
3. 点击 `Run workflow`
4. 选择分支（通常是 `main`）
5. 点击绿色的 `Run workflow` 按钮

---

## 📊 查看运行结果

### 查看执行日志
1. 进入 `Actions` 标签
2. 点击最近的 workflow 运行记录
3. 查看每个步骤的详细日志

### 查看更新的数据
1. 进入 `data/` 目录
2. 查看 `prices.json` 和 `history.json` 的提交记录
3. 每次自动运行后会有新的 commit：
   ```
   🤖 Auto update prices - 2026-01-29
   ```

---

## 🔧 高级配置

### 修改运行时间

编辑 `.github/workflows/daily-price-scraper.yml`：

```yaml
on:
  schedule:
    # 例如：改为每天 2:00 AM (UTC 07:00)
    - cron: '0 7 * * *'
```

### 增加运行频率

```yaml
on:
  schedule:
    # 每天 00:00 和 12:00 运行两次
    - cron: '0 5 * * *'   # 00:00 EST
    - cron: '0 17 * * *'  # 12:00 EST
```

### 禁用自动运行

将 workflow 文件重命名或删除 `schedule` 部分，只保留 `workflow_dispatch`（手动触发）。

---

## 🐛 故障排查

### 问题 1: Workflow 未运行
**原因**：仓库长时间无活动会被暂停
**解决**：
- 手动触发一次 workflow 即可重新激活
- 或者定期（60天内）推送一次代码

### 问题 2: 推送失败 (Permission denied)
**原因**：Workflow 权限不足
**解决**：
1. 检查 Settings → Actions → General → Workflow permissions
2. 确保选择了 `Read and write permissions`

### 问题 3: Playwright 浏览器安装失败
**原因**：依赖缺失或网络问题
**解决**：
- 查看 workflow 日志中的错误信息
- 通常会自动重试，GitHub Actions 网络稳定

### 问题 4: 数据未更新
**原因**：可能网站价格未变化或抓取失败
**解决**：
1. 查看 workflow 日志
2. 如果有 "No changes to commit" 表示价格未变化
3. 如果抓取失败，会上传 debug logs 到 Artifacts

---

## 📈 成本说明

### GitHub Actions 免费额度
- **Public 仓库**：无限制，完全免费
- **Private 仓库**：
  - 每月 2,000 分钟免费
  - 本项目每次运行约 5-10 分钟
  - 可运行 **200-400 次/月**（足够每天运行）

### 存储限制
- GitHub 仓库：单个文件 < 100MB，总大小 < 1GB
- 截图会占用空间，建议定期清理旧截图

---

## 🔐 安全建议

1. **使用 Private 仓库**：如果数据敏感
2. **不要提交敏感信息**：
   - 不要在代码中硬编码密码、API Key
   - 使用 GitHub Secrets 存储敏感数据
3. **定期检查 Actions 日志**：确保没有异常

---

## 🌐 与本地同步

### 从 GitHub 拉取最新数据

```bash
cd ~/Downloads/ca-price-dashboard
git pull origin main
```

### 推送本地更改

```bash
cd ~/Downloads/ca-price-dashboard
git add .
git commit -m "Update configuration"
git push origin main
```

---

## 📞 常用命令

```bash
# 查看当前状态
cd ~/Downloads/ca-price-dashboard
git status

# 查看提交历史
git log --oneline -10

# 强制同步（覆盖本地更改）
git fetch origin
git reset --hard origin/main

# 查看远程仓库
git remote -v
```

---

## ✨ 功能特点

- ✅ **完全自动化**：无需人工干预
- ✅ **云端运行**：电脑关机也能工作
- ✅ **数据持久化**：自动提交到 GitHub
- ✅ **错误处理**：失败时上传调试日志
- ✅ **时区支持**：使用加拿大东部时间
- ✅ **手动触发**：可随时手动运行
- ✅ **完全免费**：GitHub Actions 免费额度足够使用

---

## 📝 下一步

1. ✅ 完成上述部署步骤
2. ✅ 手动触发一次测试
3. ✅ 等待第二天自动运行
4. ✅ 检查数据是否正常更新

---

**部署时间**: 2026-01-29  
**维护者**: Claude + Anker  
**GitHub Actions**: [官方文档](https://docs.github.com/en/actions)
