"""
Generic RSS crawler - supports RSS/Atom feed parsing
"""
import re
import feedparser
from datetime import datetime
from typing import List, Dict, Any
import time


class RSSCrawler:
    """RSS feed crawler"""

    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.results = []

    def crawl_feed(self, name: str, url: str, category: str = "blog") -> List[Dict[str, Any]]:
        """
        Crawl single RSS feed

        Args:
            name: Data source name
            url: RSS feed URL
            category: Content category

        Returns:
            List of article dictionaries
        """
        try:
            feed = feedparser.parse(url)
            entries = []

            for entry in feed.entries[:15]:  # Get recent 15 entries
                article = {
                    "source": name,
                    "category": category,
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": self._parse_date(entry.get("published", "")),
                    "summary": self._clean_summary(entry.get("summary", "")),
                    "author": entry.get("author", ""),
                    "tags": [tag.term for tag in entry.get("tags", [])]
                }
                entries.append(article)

            time.sleep(self.delay)
            return entries

        except Exception as e:
            print(f"  [RSS] Error fetching {name}: {e}")
            return []

    def crawl_multiple(self, feeds: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Batch crawl multiple RSS feeds

        Args:
            feeds: [{"name": "...", "url": "...", "category": "..."}]

        Returns:
            All articles sorted by publish time
        """
        all_articles = []

        for feed in feeds:
            print(f"  [RSS] Fetching: {feed['name']}")
            articles = self.crawl_feed(
                name=feed["name"],
                url=feed["url"],
                category=feed.get("category", "blog")
            )
            all_articles.extend(articles)
            print(f"  [RSS] {feed['name']}: {len(articles)} articles")

        # Sort by publish time
        all_articles.sort(
            key=lambda x: x.get("published") or datetime.min,
            reverse=True
        )

        return all_articles

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string"""
        if not date_str:
            return datetime.now()

        try:
            # feedparser already parsed as time.struct_time
            if hasattr(date_str, 'tm_year'):
                return datetime(*date_str[:6])
            return datetime.now()
        except Exception:
            return datetime.now()

    def _clean_summary(self, summary: str, max_length: int = 300) -> str:
        """Clean summary text"""
        if not summary:
            return ""

        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', summary)
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean[:max_length] + "..." if len(clean) > max_length else clean


# Predefined RSS feeds (corresponds to sources.yaml)
DEFAULT_FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/news/rss.xml", "category": "blog"},
    {"name": "HuggingFace Blog", "url": "https://huggingface.co/blog/feed.xml", "category": "blog"},
    {"name": "BAIR Blog", "url": "http://bair.berkeley.edu/blog/feed.xml", "category": "blog"},
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/", "category": "blog"},
    {"name": "Interconnects", "url": "https://www.interconnects.ai/feed", "category": "blog"},
    {"name": "Sebastian Raschka", "url": "https://magazine.sebastianraschka.com/feed", "category": "blog"},
    {"name": "a16z AI", "url": "https://a16z.com/feed/", "category": "blog"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "category": "news"},
]
