#!/usr/bin/env python3
"""
AI News Crawler - Main Entry Point

Usage:
    python scripts/crawl.py [--config PATH] [--output-dir DIR]
"""
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

import yaml

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spiders.rss_spider import RSSCrawler, DEFAULT_FEEDS
from spiders.arxiv_spider import ArXivCrawler
from spiders.github_spider import GitHubCrawler
from processors.deduplicator import Deduplicator
from processors.report_generator import ReportGenerator


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
                    "categories": ["cs.AI", "cs.LG", "cs.CL"],
                    "max_results": 15,
                    "days_back": 3
                }
            },
            "github_trending": {
                "enabled": True,
                "config": {
                    "languages": ["", "python", "javascript", "rust"],
                    "since": "daily"
                }
            },
            "rss_feeds": DEFAULT_FEEDS
        },
        "settings": {
            "request_delay": 1.0,
            "max_retries": 3,
            "timeout": 30
        },
        "deduplication": {
            "simhash_threshold": 3
        }
    }

    if config_path is None or not os.path.exists(config_path):
        default_paths = [
            os.path.join(os.path.dirname(__file__), "..", "config", "sources.yaml"),
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
            print(f"[Config] Loaded: {config_path}")
        except Exception as e:
            print(f"[Config] Warning: Failed to load config: {e}, using defaults")
    else:
        print("[Config] Using default configuration")

    return default_config


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
        output_dir = "/mnt/user-data/outputs/ai-news"

    settings = config.get("settings", {})
    sources = config.get("sources", {})

    print("=" * 50)
    print("AI News Crawler")
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
            arxiv_crawler = ArXivCrawler()
            arxiv_cfg = arxiv_config.get("config", {})
            arxiv_articles = arxiv_crawler.crawl(
                categories=arxiv_cfg.get("categories", ["cs.AI", "cs.LG", "cs.CL"]),
                max_results=arxiv_cfg.get("max_results", 15),
                days_back=arxiv_cfg.get("days_back", 3)
            )
            all_articles.extend(arxiv_articles)
        except Exception as e:
            print(f"[ArXiv] Error: {e}")

    # 3. Crawl GitHub Trending
    github_config = sources.get("github_trending", {})
    if github_config.get("enabled", True):
        print("\n[Phase 3] Crawling GitHub Trending...")
        try:
            github_crawler = GitHubCrawler()
            gh_cfg = github_config.get("config", {})
            github_repos = github_crawler.crawl(
                languages=gh_cfg.get("languages", ["", "python", "javascript", "rust"]),
                since=gh_cfg.get("since", "daily")
            )
            all_articles.extend(github_repos)
        except Exception as e:
            print(f"[GitHub] Error: {e}")

    print(f"\n[Summary] Total articles fetched: {len(all_articles)}")

    # 4. Deduplication
    print("\n[Phase 4] Deduplicating...")
    dedup_config = config.get("deduplication", {})
    deduplicator = Deduplicator(
        simhash_threshold=dedup_config.get("simhash_threshold", 3)
    )
    unique_articles = deduplicator.deduplicate(all_articles)

    # 5. Generate report
    print("\n[Phase 5] Generating report...")
    generator = ReportGenerator()
    html = generator.generate(unique_articles)

    # 6. Save file
    timestamp = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"ai-news-{timestamp}.html")
    generator.save(html, output_path)

    print("\n" + "=" * 50)
    print(f"Done! {len(unique_articles)} unique articles")
    print(f"Report: {output_path}")
    print("=" * 50)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="AI News Crawler")
    parser.add_argument(
        "--config",
        default=None,
        help="Config file path (default: config/sources.yaml)"
    )
    parser.add_argument(
        "--output-dir",
        default="/mnt/user-data/outputs/ai-news",
        help="Output directory (default: /mnt/user-data/outputs/ai-news)"
    )

    args = parser.parse_args()
    run_crawler(args.config, args.output_dir)


if __name__ == "__main__":
    main()
