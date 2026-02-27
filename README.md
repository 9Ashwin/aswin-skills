# Aswin Skills

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## English

Claude Code Skills repository for code review and development.

### Installation

```bash
# Install via npx skills
npx skills add https://github.com/ashwinyue/aswin-skills.git --skill git-review

# Or install globally
npx skills add https://github.com/ashwinyue/aswin-skills.git --skill git-review -g
```

### Available Skills

| Skill | Description |
|-------|-------------|
| [git-review](skills/git-review/) | Local code review tool for pre-push self-check |

---

<a name="中文"></a>

## 中文

Claude Code Skills 仓库，提供代码审查和开发相关的共享技能。

### 安装

```bash
# 通过 npx skills 安装
npx skills add https://github.com/ashwinyue/aswin-skills.git --skill git-review

# 或全局安装
npx skills add https://github.com/ashwinyue/aswin-skills.git --skill git-review -g
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
