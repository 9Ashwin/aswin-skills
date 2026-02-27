# SCM Skills

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## English

Claude Code Skills repository for the Seat team, providing shared skills for code review and development.

### Installation

> **Note**: `npx skills add` is not supported due to Gogs shallow clone limitation. Use the script below.

```bash
# One-click install
curl -sSL https://gogs.maizuo.com/seat/scm-skills/raw/main/install.sh | bash
```

### Available Skills

| Skill | Description |
|-------|-------------|
| [git-review](git-review/) | Local code review tool for pre-push self-check |

---

<a name="中文"></a>

## 中文

Seat 团队的 Claude Code Skills 仓库，提供代码审查和开发相关的共享技能。

### 安装

> **注意**: 由于 Gogs 不支持浅克隆，`npx skills add` 无法使用。请使用以下脚本安装。

```bash
# 一键安装
curl -sSL https://gogs.maizuo.com/seat/scm-skills/raw/main/install.sh | bash
```

### 可用 Skills

| Skill | 描述 |
|-------|------|
| [git-review](git-review/) | 本地代码审查工具，用于 push 前自检 |

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
