# Seat Skills

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## English

Claude Code Skills repository for the Seat team, providing shared skills for code review and development.

### Prerequisites

- Node.js environment installed
- Ability to run `npx` commands

### Installation

#### Quick Install (推荐)

```bash
# 一键安装 git-review skill
curl -sSL https://gogs.maizuo.com/seat/skills/raw/main/install.sh | bash

# 安装指定 skill
curl -sSL https://gogs.maizuo.com/seat/skills/raw/main/install.sh | bash -s git-review
```

#### Manual Install

```bash
git clone https://gogs.maizuo.com/seat/skills.git /tmp/seat-skills
cp -r /tmp/seat-skills/skills/git-review ~/.claude/skills/
```

### Available Skills

| Skill | Description |
|-------|-------------|
| [git-review](skills/git-review/) | Local code review tool for pre-push self-check |

### Skills Structure

```
skills/
├── <skill-name>/
│   ├── SKILL.md          # Core file (required)
│   ├── references/       # Reference docs (optional)
│   ├── scripts/          # Script files (optional)
│   └── prompts/          # Prompt templates (optional)
```

### Contributing

1. Fork this repository
2. Create a new skill in `skills/` directory
3. Submit a PR

---

<a name="中文"></a>

## 中文

Seat 团队的 Claude Code Skills 仓库，提供代码审查和开发相关的共享技能。

### 前置条件

- 已安装 Node.js 环境
- 能够运行 `npx` 命令

### 安装

#### 一键安装 (推荐)

```bash
# 安装 git-review skill
curl -sSL https://gogs.maizuo.com/seat/skills/raw/main/install.sh | bash

# 安装指定 skill
curl -sSL https://gogs.maizuo.com/seat/skills/raw/main/install.sh | bash -s git-review
```

#### 手动安装

```bash
git clone https://gogs.maizuo.com/seat/skills.git /tmp/seat-skills
cp -r /tmp/seat-skills/skills/git-review ~/.claude/skills/
```

### 可用 Skills

| Skill | 描述 |
|-------|------|
| [git-review](skills/git-review/) | 本地代码审查工具，用于 push 前自检 |

### 审查范围

| 范围 | Git 命令 | 场景 |
|------|----------|------|
| 未暂存 | `git diff` | 检查工作区修改 |
| 已暂存未提交 | `git diff --cached` | commit 前检查 |
| 已提交未推送 | `git diff origin/$(git branch --show-current)` | push 前检查 |

### 审查风格

| 风格 | 描述 |
|------|------|
| professional | 专业严谨，使用标准工程术语（默认）|
| sarcastic | 讽刺风格，技术指正准确 |
| gentle | 温和风格，多用"建议"、"可以考虑" |
| humorous | 幽默风格，适当使用 Emoji |

### 评分标准

| 维度 | 分值 |
|------|------|
| 功能正确性与健壮性 | 40分 |
| 安全性与潜在风险 | 30分 |
| 最佳实践 | 20分 |
| 性能与资源利用 | 5分 |
| Commits 信息清晰性 | 5分 |

### Skills 结构

```
skills/
├── <skill-name>/
│   ├── SKILL.md          # 核心文件（必需）
│   ├── references/       # 参考文档（可选）
│   ├── scripts/          # 脚本文件（可选）
│   └── prompts/          # 提示词模板（可选）
```

### 贡献

1. Fork 本仓库
2. 在 `skills/` 目录下创建新的 skill
3. 提交 PR
