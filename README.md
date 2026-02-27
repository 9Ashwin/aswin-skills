# Seat Skills

Claude Code Skills 仓库，用于存放团队共享的技能。

## 安装

```bash
# 安装单个 skill
npx skills add https://gogs.maizuo.com/seat/skills --skill <skill-name>

# 示例：安装 git-review
npx skills add https://gogs.maizuo.com/seat/skills --skill git-review
```

## 可用 Skills

| Skill | 描述 |
|-------|------|
| [git-review](skills/git-review/) | 本地代码审查工具，用于 push 前自检 |

## Skills 结构

```
skills/
├── <skill-name>/
│   ├── SKILL.md          # 核心文件（必需）
│   ├── references/       # 参考文档（可选）
│   ├── scripts/          # 脚本文件（可选）
│   └── prompts/          # 提示词模板（可选）
```

## 贡献

1. Fork 本仓库
2. 在 `skills/` 目录下创建新的 skill
3. 提交 PR
