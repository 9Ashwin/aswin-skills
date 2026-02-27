#!/bin/bash

# SCM Skills 安装脚本
# 用法: curl -sSL https://gogs.maizuo.com/seat/scm-skills/raw/main/install.sh | bash

REPO_URL="https://gogs.maizuo.com/seat/scm-skills.git"
SKILL_NAME="${1:-git-review}"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"

echo "🚀 安装 SCM Skills: $SKILL_NAME"

# 创建临时目录
TEMP_DIR=$(mktemp -d)

# 克隆仓库（不使用 --depth 1，因为 Gogs 不支持浅克隆）
echo "📦 克隆仓库..."
if ! git clone "$REPO_URL" "$TEMP_DIR" 2>/dev/null; then
    echo "❌ 克隆失败，请检查网络连接或仓库权限"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 检查 skill 是否存在
if [ ! -d "$TEMP_DIR/$SKILL_NAME" ]; then
    echo "❌ Skill '$SKILL_NAME' 不存在"
    echo "可用的 skills:"
    ls -1 "$TEMP_DIR" | grep -v "^\." | grep -v "^README" | grep -v "^CHANGELOG" | grep -v "^install"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 确保目标目录存在
mkdir -p "$CLAUDE_SKILLS_DIR"

# 如果已存在，先删除
if [ -d "$CLAUDE_SKILLS_DIR/$SKILL_NAME" ]; then
    echo "🔄 更新已存在的 $SKILL_NAME..."
    rm -rf "$CLAUDE_SKILLS_DIR/$SKILL_NAME"
fi

# 安装 skill
echo "📥 安装 $SKILL_NAME..."
cp -r "$TEMP_DIR/$SKILL_NAME" "$CLAUDE_SKILLS_DIR/"

# 清理
rm -rf "$TEMP_DIR"

echo "✅ 安装完成!"
echo ""
echo "使用方式:"
echo "  - review 我的代码"
echo "  - 检查代码变更"
echo "  - git review"
