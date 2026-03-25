---
name: ai-news-crawler
description: "AI技术日报生成器 - 专为开发者设计。聚合 ArXiv 论文、GitHub 热门项目、技术博客，支持LLM深度摘要，自动提取技术亮点、代码链接，生成开发者友好的技术日报。触发词: 'AI技术日报', '开发者AI新闻', '技术论文汇总', 'crawl AI news', '今日AI资讯', 'AI新闻聚合', '技术趋势报告', '生成AI日报', 'AI paper summary', 'github trending report', 'arxiv daily', 'AI技术博客汇总'"

compatibility: Requires Python 3.8+, Claude Code CLI installed, feedparser, arxiv, beautifulsoup4, lxml, requests, jinja2, pyyaml. Bash and file write tools required.
---

# AI News Crawler - Developer Edition

> 专为程序员和 AI 工程师设计的技术日报生成器

## 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **6大技术分类** | LLM、论文、代码、工具、基础设施、教程 |
| 🧠 **LLM深度摘要** | 使用 Claude/GPT 生成整体趋势洞察和分类摘要 |
| 📊 **智能摘要** | 自动提取技术亮点、性能指标、架构创新 |
| 🔗 **代码链接** | 自动识别论文中的 GitHub/HuggingFace 代码 |
| 📈 **复杂度评估** | 标注论文难度（入门/中等/高阶） |
| 🚀 **实用性标记** | 评估是否可直接用于生产环境 |
| 🎨 **开发者UI** | 代码高亮、一键复制、响应式暗色主题 |

## AI 深度摘要功能

本 Skill 支持调用 LLM 生成深度技术趋势分析，使用 `claude code` CLI 工具（而非直接调用 API）。

### 配置要求

需要确保 Claude Code CLI 已安装：

```bash
# 检查是否已安装（如果已安装，会显示版本号）
claude --version

# 如果未安装，执行以下命令安装：
# 方式1：npm
npm install -g @anthropic-ai/claude-code

# 方式2：官方安装器
curl -sSL https://claude.ai/install | sh
```

> **注意**：只需安装一次。如果已经安装过 Claude Code CLI，无需重复安装。

### 可选配置

```bash
# 指定使用的模型（可选，默认使用 claude 的默认模型）
export CLAUDE_MODEL=claude-sonnet-4-6
```

### LLM 摘要内容

- **整体趋势洞察**: 宏观分析今日 AI 领域趋势和热点方向
- **GitHub 趋势**: 开源项目技术方向、热门类型、新特性
- **论文热点**: 研究方向、技术创新点、潜在应用价值
- **博客动态**: 产品发布、行业观点、开发者关注话题

### 使用示例

```python
from main import run_crawler

# LLM 摘要会自动启用（如果 claude code CLI 已安装）
report_path = run_crawler()

# 或者在 main.py 中控制
summarizer = TechSummarizer()
overall, categories = summarizer.summarize(
    articles,
    use_llm=True,           # 启用 LLM
    llm_provider="anthropic"  # 选择提供商
)
```

## 技术分类体系

```
🤖 LLM/模型
   └─ GPT/Claude/Llama 更新、RAG、Agent、Prompt 技术

📄 前沿论文
   └─ ArXiv 最新论文，带技术亮点提取和代码链接

💻 开源代码
   └─ GitHub Trending，按语言分类

🛠️ 开发工具
   └─ SDK、API、框架、CLI 工具更新

⚙️ 基础设施
   └─ 部署优化、推理加速、模型压缩

📚 技术教程
   └─ 最佳实践、教程、案例研究
```

## 快速开始

### 命令行

```bash
# 默认配置运行
python main.py

# 自定义配置
python main.py --config config/sources.yaml --output-dir ./reports
```

### Python API

```python
from main import run_crawler

# 运行爬虫
report_path = run_crawler()
print(f"报告已生成: {report_path}")
```

## 输出示例

```
==================================================
AI News Crawler - Developer Edition
==================================================

[Phase 1] Crawling RSS feeds...
[Phase 2] Crawling ArXiv papers...
  [ArXiv] Fetching cs.AI...
  [ArXiv] Fetching cs.LG...
  [ArXiv] Fetched 45 papers
[Phase 3] Crawling GitHub Trending...

[Summary] Total articles fetched: 127

[Phase 4] Classifying for developers...
[Phase 5] Deduplicating...
[Phase 6] Generating tech summaries...
[Phase 7] Generating report...
  [Report] Saved to: ./output/ai-news-20250325.html

==================================================
Done! 89 unique articles

Category breakdown:
  🤖 LLM/模型: 23
  📄 前沿论文: 34
  💻 开源代码: 15
  🛠️ 开发工具: 8
  ⚙️ 基础设施: 5
  📚 技术教程: 4

Report: ./output/ai-news-20250325.html
==================================================
```

## 论文技术亮点提取

系统自动从论文摘要中提取：

| 类型 | 示例 |
|------|------|
| **性能提升** | "性能: 2.5x 提升", "性能: 35% 提升" |
| **架构创新** | "架构: TRANSFORMER", "架构: MOE" |
| **模型规模** | "规模: 70B parameters" |
| **能力特点** | "能力: multimodal", "能力: RAG" |

## 项目结构

```
ai-news-crawler/
├── SKILL.md                    # 本文件
├── main.py                     # 主入口（含开发者分类逻辑）
├── scripts/
│   └── crawl.py               # CLI 脚本
├── requirements.txt            # 依赖
├── config/
│   └── sources.yaml           # 数据源配置
├── assets/
│   └── report_template.html   # 开发者主题模板
├── spiders/                   # 爬虫模块
│   ├── __init__.py
│   ├── arxiv_spider.py       # ArXiv + 技术亮点提取
│   ├── github_spider.py      # GitHub Trending
│   └── rss_spider.py         # RSS 技术博客
└── processors/               # 数据处理
    ├── __init__.py
    ├── deduplicator.py      # URL + SimHash 去重
    ├── report_generator.py  # HTML 报告生成
    └── tech_summarizer.py   # 技术摘要生成
```

## 配置示例

```yaml
# config/sources.yaml
sources:
  arxiv_ai:
    enabled: true
    config:
      categories: ["cs.AI", "cs.LG", "cs.CL", "cs.SE", "cs.SY"]
      max_results: 20
      days_back: 3
      fetch_code_links: true    # 提取代码链接

  github_trending:
    enabled: true
    config:
      languages: ["python", "rust", "typescript", "go", ""]
      since: "daily"
      min_stars: 50

  rss_feeds:
    # 技术博客 RSS 源
    - name: "Distill.pub"
      url: "https://distill.pub/rss.xml"
      category: "blog"
    - name: "Lil'Log"
      url: "https://lilianweng.github.io/rss.xml"
      category: "blog"

settings:
  request_delay: 1.0           # 请求间隔（秒），避免rate limiting
  max_retries: 3              # 失败重试次数

output:
  generate_tech_summary: true    # 生成AI技术摘要
  include_code_snippets: true    # 包含代码片段
```

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `request_delay` | float | 1.0 | 请求间隔秒数，增加此值可降低被rate limit的风险 |
| `max_retries` | int | 3 | 请求失败时的重试次数，支持指数退避 |
| `max_results` | int | 20 | 每个ArXiv分类获取的最大论文数 (1-100) |
| `days_back` | int | 3 | 获取最近N天的论文 (1-30) |
| `since` | string | "daily" | GitHub trending 时间范围: daily/weekly/monthly |
| `min_stars` | int | 50 | GitHub项目最小star数筛选 |

## 开发者分类规则

自动根据标题、摘要、标签分类：

```python
# LLM 相关关键词
llm_keywords = [
    "gpt", "claude", "llama", "gemini", "mistral",
    "transformer", "rag", "agent", "prompt", "fine-tuning"
]

# 基础设施关键词
infra_keywords = [
    "deployment", "inference", "optimization", "quantization",
    "tensorrt", "vllm", "distributed", "kubernetes"
]

# 工具关键词
tool_keywords = [
    "sdk", "api", "framework", "cli", "vscode", "plugin"
]
```

## HTML 报告特性

### 论文卡片
- 📊 技术亮点标签（性能/架构/规模/能力）
- 🎯 复杂度标记（入门/中等/高阶）
- 🚀 实用性评估（可直接用于生产/有实现潜力/理论研究）
- 📦 代码仓库链接（GitHub/HuggingFace）
- 📋 一键复制 ArXiv 引用

### 开源项目卡片
- ⭐ Star 数及今日新增
- 🔤 编程语言标签
- 📝 项目简介

### 界面功能
- 🌙 暗色/亮色主题自动切换
- 📱 移动端适配
- 🔍 Tab 分类浏览
- 📋 一键复制标题

## 扩展开发

### 添加新数据源

```python
# spiders/custom_spider.py
class CustomCrawler:
    def crawl(self) -> List[Dict]:
        return [{
            "source": "Custom Source",
            "dev_category": "llm",  # 开发者分类
            "title": "...",
            "url": "...",
            "summary": "...",
            "tags": ["tag1", "tag2"],
            "metadata": {
                "tech_highlights": ["性能: 2x 提升"],
                "complexity": "中等",
                "applicability": "可直接用于生产"
            }
        }]
```

### 自定义分类规则

```python
# 在 main.py 的 classify_for_developers 中添加
def classify_for_developers(article: dict) -> str:
    text = f"{title} {summary}"

    # 你的自定义规则
    if "your-keyword" in text:
        return "your-category"

    # ... 其他规则
```

## 技术依赖

```
# 核心依赖（数据爬取和处理）
arxiv>=1.4
feedparser>=6.0
beautifulsoup4>=4.9
requests>=2.28
jinja2>=3.1
pyyaml>=6.0
lxml>=4.9

# LLM 摘要依赖（命令行工具，非 Python 包）
# 需要安装 Claude Code CLI:
#   npm install -g @anthropic-ai/claude-code
#   或: curl -sSL https://claude.ai/install | sh
```

## 质量检查清单

### 数据质量
- [ ] ArXiv 论文包含技术亮点
- [ ] 代码链接正确提取
- [ ] 复杂度评估准确
- [ ] 去重后无重复内容

### 报告质量
- [ ] 6个分类正确分组
- [ ] 技术摘要生成成功
- [ ] HTML 样式正常（暗色主题）
- [ ] 复制按钮功能正常

### 内容质量
- [ ] 论文卡片显示技术亮点
- [ ] 代码链接可点击
- [ ] 分类统计准确
- [ ] 日期格式正确

## 故障排除

| 问题 | 解决 |
|------|------|
| ArXiv API 失败 | 检查网络，API 通常稳定 |
| 技术亮点未显示 | 检查论文摘要是否包含指标信息 |
| 代码链接未提取 | 确保论文摘要包含 GitHub URL |
| 分类不准确 | 调整 `classify_for_developers` 中的关键词 |
| LLM 摘要失败 | 确保 `claude` 命令已安装并可执行 (`claude --version`) |
| claude code 超时 | 检查网络连接，或增加 timeout 值（默认5分钟） |

## 高级配置

### 自定义 RSS 源

编辑 `config/sources.yaml`：

```yaml
sources:
  rss_feeds:
    - name: "My Favorite Blog"
      url: "https://example.com/rss.xml"
      category: "blog"
    - name: "AI Research Lab"
      url: "https://lab.example.com/feed"
      category: "news"
```

### 自定义分类规则

在 `main.py` 中修改 `classify_for_developers` 函数：

```python
def classify_for_developers(article: dict) -> str:
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()

    # 添加你的自定义规则
    if "security" in title or "safety" in title:
        return "security"  # 新增安全分类

    # ... 其他规则
```

### 添加新的爬虫源

1. 在 `spiders/` 创建新的爬虫文件
2. 实现 `crawl()` 方法返回文章列表
3. 在 `main.py` 中导入并调用

示例：

```python
# spiders/huggingface_spider.py
class HuggingFaceCrawler:
    def crawl(self) -> List[Dict]:
        # 实现爬取逻辑
        return [{
            "source": "HuggingFace",
            "category": "model",
            "title": "...",
            "url": "...",
            "summary": "..."
        }]
```

### 修改报告模板

编辑 `assets/report_template.html`：
- 自定义 CSS 样式
- 添加/删除显示字段
- 修改颜色主题

### 配置代理

如需使用代理访问外网：

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
python main.py
```

## 相关项目

- 参考了 `.agents/skills/daily-ai-news` 的输出模板设计
- 针对开发者场景进行了深度定制
