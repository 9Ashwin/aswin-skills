#!/bin/bash

# Seat Skills 安装脚本
# 用法: curl -sSL https://gogs.maizuo.com/seat/skills/raw/main/install.sh | bash

set -e

REPO_URL="https://gogs.maizuo.com/seat/skills.git"
TEMP_DIR=$(mktemp -d)
SKILL_NAME="${1:-git-review}"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"

echo "🚀 安装 Seat Skills: $SKILL_NAME"

# 克隆仓库
echo "📦 克隆仓库..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR"

# 确保目标目录存在
mkdir -p "$CLAUDE_SKILLS_DIR"

# 检查 skill 是否存在
if [ ! -d "$TEMP_DIR/skills/$SKILL_NAME" ]; then
    echo "❌ Skill '$SKILL_NAME' 不存在"
    echo "可用的 skills:"
    ls -1 "$TEMP_DIR/skills/"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 安装 skill
echo "📥 安装 $SKILL_NAME..."
cp -r "$TEMP_DIR/skills/$SKILL_NAME" "$CLAUDE_SKILLS_DIR/"

# 清理
rm -rf "$TEMP_DIR"

echo "✅ 安装完成!"
echo ""
echo "使用方式:"
echo "  - review 我的代码"
echo "  - 检查代码变更"
echo "  - git review"
