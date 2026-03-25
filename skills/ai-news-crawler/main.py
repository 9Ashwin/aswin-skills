"""
AI News Crawler - Main Entry Point

Usage:
    python main.py [--config PATH] [--output-dir DIR]
"""
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiders.rss_spider import RSSCrawler, DEFAULT_FEEDS
from spiders.arxiv_spider import ArXivCrawler
from spiders.github_spider import GitHubCrawler
from processors.deduplicator import Deduplicator
from processors.report_generator import ReportGenerator
from processors.tech_summarizer import TechSummarizer


def validate_config(config: dict) -> list:
    """
    Validate configuration and return list of errors

    Args:
        config: Configuration dictionary

    Returns:
        List of validation error messages
    """
    errors = []

    # Validate sources
    sources = config.get("sources", {})

    # ArXiv config validation
    arxiv_cfg = sources.get("arxiv_ai", {}).get("config", {})
    if arxiv_cfg:
        max_results = arxiv_cfg.get("max_results", 20)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
            errors.append("arxiv_ai.config.max_results must be an integer between 1 and 100")

        days_back = arxiv_cfg.get("days_back", 3)
        if not isinstance(days_back, int) or days_back < 1 or days_back > 30:
            errors.append("arxiv_ai.config.days_back must be an integer between 1 and 30")

    # GitHub config validation
    github_cfg = sources.get("github_trending", {}).get("config", {})
    if github_cfg:
        since = github_cfg.get("since", "daily")
        if since not in ["daily", "weekly", "monthly"]:
            errors.append("github_trending.config.since must be 'daily', 'weekly', or 'monthly'")

        min_stars = github_cfg.get("min_stars", 50)
        if not isinstance(min_stars, int) or min_stars < 0:
            errors.append("github_trending.config.min_stars must be a non-negative integer")

    # Settings validation
    settings = config.get("settings", {})
    request_delay = settings.get("request_delay", 1.0)
    if not isinstance(request_delay, (int, float)) or request_delay < 0:
        errors.append("settings.request_delay must be a non-negative number")

    max_retries = settings.get("max_retries", 3)
    if not isinstance(max_retries, int) or max_retries < 0 or max_retries > 10:
        errors.append("settings.max_retries must be an integer between 0 and 10")

    return errors


def load_config(config_path: str = None) -> dict:
    """
    Load YAML configuration file

    Args:
        config_path: Path to config file, None to use defaults

    Returns:
        Configuration dictionary
    """
    default_config = {
        "sources": {
            "arxiv_ai": {
                "enabled": True,
                "config": {
                    "categories": ["cs.AI", "cs.LG", "cs.CL", "cs.SE", "cs.SY"],
                    "max_results": 20,
                    "days_back": 3,
                    "fetch_code_links": True
                }
            },
            "github_trending": {
                "enabled": True,
                "config": {
                    "languages": ["python", "rust", "typescript", "go", ""],
                    "since": "daily",
                    "min_stars": 50
                }
            },
            "rss_feeds": DEFAULT_FEEDS,
            "tech_blogs": {
                "enabled": True,
                "config": {
                    "blogs": [
                        "distill",
                        "lil_log",
                        "sebastian_raschka",
                        "huggingface",
                        "openai",
                        "anthropic"
                    ]
                }
            }
        },
        "settings": {
            "request_delay": 1.0,
            "max_retries": 3,
            "timeout": 30
        },
        "deduplication": {
            "simhash_threshold": 3
        },
        "output": {
            "generate_tech_summary": True,
            "include_code_snippets": True,
            "highlight_complexity": True
        }
    }

    if config_path is None or not os.path.exists(config_path):
        default_paths = [
            os.path.join(os.path.dirname(__file__), "config", "sources.yaml"),
            "/mnt/skills/ai-news-crawler/config/sources.yaml"
        ]
        for path in default_paths:
            if os.path.exists(path):
                config_path = path
                break

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
            default_config["sources"].update(user_config.get("sources", {}))
            default_config["settings"].update(user_config.get("settings", {}))
            default_config["deduplication"].update(user_config.get("deduplication", {}))
            default_config["output"].update(user_config.get("output", {}))
            print(f"[Config] Loaded: {config_path}")
        except Exception as e:
            print(f"[Config] Warning: Failed to load config: {e}, using defaults")
    else:
        print("[Config] Using default configuration")

    # Validate configuration
    errors = validate_config(default_config)
    if errors:
        print("[Config] Validation errors:")
        for error in errors:
            print(f"  - {error}")
        print("[Config] Using default values for invalid settings")

    return default_config


def classify_for_developers(article: dict) -> str:
    """
    技术导向的分类 - 专为程序员设计

    分类规则：
    - llm: 大语言模型相关
    - paper: 学术研究论文
    - code: 开源代码/项目
    - tool: 开发工具/SDK
    - infra: 基础设施/部署
    - tutorial: 技术教程
    """
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    source = article.get("source", "").lower()
    tags = [t.lower() for t in article.get("tags", [])]

    text = f"{title} {summary} {' '.join(tags)}"

    # LLM/模型相关
    llm_keywords = ["gpt", "claude", "llama", "gemini", "mistral", "transformer",
                    "language model", "fine-tuning", "prompt", "rag", "agent"]
    if any(k in text for k in llm_keywords):
        return "llm"

    # 基础设施/部署
    infra_keywords = ["deployment", "inference", "optimization", "quantization",
                      "tensorrt", "onnx", "vllm", "cuda", "gpu", "serving",
                      "distributed", "training", "kubernetes", "docker"]
    if any(k in text for k in infra_keywords):
        return "infra"

    # 开发工具
    tool_keywords = ["sdk", "api", "framework", "library", "toolkit", "cli",
                     "vscode", "plugin", "extension", "debugger", "profiler"]
    if any(k in text for k in tool_keywords):
        return "tool"

    # 教程
    tutorial_keywords = ["tutorial", "guide", "how to", "getting started",
                         "best practice", "example", "walkthrough", " explained"]
    if any(k in text for k in tutorial_keywords):
        return "tutorial"

    # 根据来源判断
    if "github" in source:
        return "code"
    if "arxiv" in source:
        return "paper"

    # 默认根据 category
    category_map = {
        "paper": "paper",
        "code": "code",
        "blog": "tutorial",
        "news": "llm"
    }
    return category_map.get(article.get("category"), "llm")


def run_crawler(config_path: str = None, output_dir: str = None) -> str:
    """
    Run crawler and generate report

    Args:
        config_path: Path to configuration file
        output_dir: Output directory

    Returns:
        Path to generated HTML file
    """
    config = load_config(config_path)

    if output_dir is None:
        output_dir = "./output"

    settings = config.get("settings", {})
    sources = config.get("sources", {})
    output_config = config.get("output", {})

    print("=" * 50)
    print("AI News Crawler - Developer Edition")
    print("=" * 50)

    all_articles = []

    # 1. Crawl RSS feeds
    rss_config = sources.get("rss_feeds", DEFAULT_FEEDS)
    if rss_config:
        print("\n[Phase 1] Crawling RSS feeds...")
        rss_crawler = RSSCrawler(delay=settings.get("request_delay", 1.0))
        rss_articles = rss_crawler.crawl_multiple(rss_config)
        all_articles.extend(rss_articles)

    # 2. Crawl ArXiv
    arxiv_config = sources.get("arxiv_ai", {})
    if arxiv_config.get("enabled", True):
        print("\n[Phase 2] Crawling ArXiv papers...")
        try:
            arxiv_crawler = ArXivCrawler(
                max_retries=settings.get("max_retries", 3),
                request_delay=settings.get("request_delay", 1.0)
            )
            arxiv_cfg = arxiv_config.get("config", {})
            arxiv_articles = arxiv_crawler.crawl(
                categories=arxiv_cfg.get("categories", ["cs.AI", "cs.LG", "cs.CL", "cs.SE"]),
                max_results=arxiv_cfg.get("max_results", 20),
                days_back=arxiv_cfg.get("days_back", 3),
                fetch_code_links=arxiv_cfg.get("fetch_code_links", True)
            )
            all_articles.extend(arxiv_articles)
        except Exception as e:
            print(f"[ArXiv] Error: {e}")

    # 3. Crawl GitHub Trending
    github_config = sources.get("github_trending", {})
    if github_config.get("enabled", True):
        print("\n[Phase 3] Crawling GitHub Trending...")
        try:
            github_crawler = GitHubCrawler(
                max_retries=settings.get("max_retries", 3),
                request_delay=settings.get("request_delay", 1.0)
            )
            gh_cfg = github_config.get("config", {})
            github_repos = github_crawler.crawl(
                languages=gh_cfg.get("languages", ["python", "rust", "typescript", "go", ""]),
                since=gh_cfg.get("since", "daily"),
                min_stars=gh_cfg.get("min_stars", 50)
            )
            all_articles.extend(github_repos)
        except Exception as e:
            print(f"[GitHub] Error: {e}")

    print(f"\n[Summary] Total articles fetched: {len(all_articles)}")

    # 4. Developer-focused classification
    print("\n[Phase 4] Classifying for developers...")
    for article in all_articles:
        article["dev_category"] = classify_for_developers(article)

    # 5. Deduplication
    print("\n[Phase 5] Deduplicating...")
    dedup_config = config.get("deduplication", {})
    deduplicator = Deduplicator(
        simhash_threshold=dedup_config.get("simhash_threshold", 3)
    )
    unique_articles = deduplicator.deduplicate(all_articles)

    # 6. Generate tech summaries
    overall_summary = None
    category_summaries = {}
    key_takeaways = []
    if output_config.get("generate_tech_summary", True):
        print("\n[Phase 6] Generating tech summaries...")
        summarizer = TechSummarizer()
        overall_summary, category_summaries, unique_articles, key_takeaways = summarizer.summarize(unique_articles)

    # 7. Generate report
    print("\n[Phase 7] Generating report...")
    generator = ReportGenerator()
    html = generator.generate(
        unique_articles,
        report_date=datetime.now(),
        overall_summary=overall_summary,
        category_summaries=category_summaries,
        key_takeaways=key_takeaways,
        include_code_snippets=output_config.get("include_code_snippets", True)
    )

    # 8. Save file
    timestamp = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"ai-news-{timestamp}.html")
    generator.save(html, output_path)

    # Print category stats
    from collections import Counter
    cat_counts = Counter([a.get("dev_category", "other") for a in unique_articles])

    print("\n" + "=" * 50)
    print(f"Done! {len(unique_articles)} unique articles")
    print("\nCategory breakdown:")
    cat_names = {
        "llm": "🤖 LLM/模型",
        "paper": "📄 前沿论文",
        "code": "💻 开源代码",
        "tool": "🛠️ 开发工具",
        "infra": "⚙️ 基础设施",
        "tutorial": "📚 技术教程"
    }
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat_names.get(cat, cat)}: {count}")
    print(f"\nReport: {output_path}")
    print("=" * 50)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="AI News Crawler - Developer Edition")
    parser.add_argument(
        "--config",
        default=None,
        help="Config file path (default: config/sources.yaml)"
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory (default: ./output)"
    )

    args = parser.parse_args()
    run_crawler(args.config, args.output_dir)


if __name__ == "__main__":
    main()
