#!/bin/bash

# Seat Skills 安装脚本
# 用法: curl -sSL https://gogs.maizuo.com/seat/skills/raw/main/install.sh | bash

REPO_URL="https://gogs.maizuo.com/seat/skills.git"
SKILL_NAME="${1:-git-review}"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
MAX_RETRIES=3

echo "🚀 安装 Seat Skills: $SKILL_NAME"

# 克隆仓库（带重试）
clone_repo() {
    local temp_dir=$(mktemp -d)
    local retry=0

    while [ $retry -lt $MAX_RETRIES ]; do
        echo "📦 克隆仓库 (尝试 $((retry + 1))/$MAX_RETRIES)..."
        rm -rf "$temp_dir"
        mkdir -p "$temp_dir"

        if git clone "$REPO_URL" "$temp_dir" 2>/dev/null; then
            # 检查是否成功克隆了内容
            if [ -d "$temp_dir/skills" ] && [ "$(ls -A $temp_dir/skills 2>/dev/null)" ]; then
                echo "$temp_dir"
                return 0
            else
                echo "⚠️  克隆成功但内容为空，重试中..."
            fi
        fi

        retry=$((retry + 1))
        [ $retry -lt $MAX_RETRIES ] && sleep 2
    done

    echo "❌ 克隆失败，请检查网络连接或仓库权限"
    rm -rf "$temp_dir"
    return 1
}

# 克隆仓库
TEMP_DIR=$(clone_repo)
if [ $? -ne 0 ] || [ -z "$TEMP_DIR" ]; then
    exit 1
fi

# 确保目标目录存在
mkdir -p "$CLAUDE_SKILLS_DIR"

# 检查 skill 是否存在
if [ ! -d "$TEMP_DIR/skills/$SKILL_NAME" ]; then
    echo "❌ Skill '$SKILL_NAME' 不存在"
    echo "可用的 skills:"
    ls -1 "$TEMP_DIR/skills/" 2>/dev/null || echo "  (无)"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 如果已存在，先删除
if [ -d "$CLAUDE_SKILLS_DIR/$SKILL_NAME" ]; then
    echo "🔄 更新已存在的 $SKILL_NAME..."
    rm -rf "$CLAUDE_SKILLS_DIR/$SKILL_NAME"
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
