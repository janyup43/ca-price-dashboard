#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        CA价格看板 - GitHub Actions 自动部署设置向导           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查是否在正确的目录
if [ ! -f "scraper_stealth.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ 错误：未安装 Git"
    echo "请访问: https://git-scm.com/downloads"
    exit 1
fi

echo "📋 步骤 1/4: 检查 Git 仓库状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d .git ]; then
    echo "初始化 Git 仓库..."
    git init
    echo "✅ Git 仓库初始化完成"
else
    echo "✅ Git 仓库已存在"
fi

echo ""
echo "📋 步骤 2/4: 提交所有文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

git add .
git commit -m "🎉 Initial commit - CA Price Dashboard with GitHub Actions"
echo "✅ 文件已提交到本地仓库"

echo ""
echo "📋 步骤 3/4: 配置远程仓库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请先在 GitHub 上创建仓库:"
echo "  1. 访问: https://github.com/new"
echo "  2. Repository name: ca-price-dashboard"
echo "  3. Privacy: Private (推荐)"
echo "  4. 不要勾选 'Initialize this repository with'"
echo "  5. 点击 'Create repository'"
echo ""
read -p "已创建 GitHub 仓库？(y/n): " created

if [ "$created" != "y" ]; then
    echo "请先创建 GitHub 仓库，然后重新运行此脚本"
    exit 0
fi

echo ""
read -p "请输入你的 GitHub 用户名: " username

if [ -z "$username" ]; then
    echo "❌ 用户名不能为空"
    exit 1
fi

REMOTE_URL="https://github.com/$username/ca-price-dashboard.git"
echo ""
echo "远程仓库 URL: $REMOTE_URL"

# 检查是否已有远程仓库
if git remote | grep -q origin; then
    echo "更新远程仓库 URL..."
    git remote set-url origin $REMOTE_URL
else
    echo "添加远程仓库..."
    git remote add origin $REMOTE_URL
fi

echo "✅ 远程仓库配置完成"

echo ""
echo "📋 步骤 4/4: 推送代码到 GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "正在推送代码..."

git branch -M main

if git push -u origin main 2>&1; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                     🎉 部署成功！                               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "✅ 代码已推送到 GitHub"
    echo ""
    echo "📝 下一步操作:"
    echo ""
    echo "1. 访问你的仓库: https://github.com/$username/ca-price-dashboard"
    echo ""
    echo "2. 配置 Actions 权限:"
    echo "   - 点击 Settings → Actions → General"
    echo "   - Workflow permissions → 选择 'Read and write permissions'"
    echo "   - 点击 Save"
    echo ""
    echo "3. 测试自动化:"
    echo "   - 点击 Actions 标签"
    echo "   - 选择 'Daily Price Scraper'"
    echo "   - 点击 'Run workflow' 手动测试"
    echo ""
    echo "4. 等待每天 00:00 (加拿大东部时间) 自动运行"
    echo ""
    echo "📖 完整文档: GITHUB_ACTIONS_SETUP.md"
    echo ""
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "可能的原因:"
    echo "1. 需要 GitHub 个人访问令牌 (Personal Access Token)"
    echo "2. 仓库 URL 不正确"
    echo "3. 网络问题"
    echo ""
    echo "📖 详细解决方案请查看: GITHUB_ACTIONS_SETUP.md"
    echo ""
fi
