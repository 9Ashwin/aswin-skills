---
name: ai-news-crawler
description: Aggregate and crawl AI news from multiple sources (ArXiv, GitHub Trending, RSS feeds) and generate daily HTML reports. Use this skill when the user mentions "AI news", "crawl papers", "generate daily report", "trending repos", or wants to aggregate AI content from multiple sources into a formatted report.

**Trigger this skill proactively when:**
- User says "crawl AI news", "generate AI daily report", "get latest papers"
- User asks about trending AI repos, recent research papers, or AI blog updates
- User wants to aggregate AI news from multiple sources into a report
- Before any task requiring up-to-date AI landscape awareness

compatibility: Requires Python 3.8+, feedparser, arxiv, beautifulsoup4, lxml, requests, jinja2, pyyaml. Web fetch, bash, and file write tools required.
---

# AI News Crawler Skill

## Overview

This skill aggregates AI-related news and content from multiple authoritative sources, generating a formatted HTML daily report. It eliminates duplicate content and organizes articles by category for easy consumption.

## Supported Data Sources

| Type | Source | Method |
|------|--------|--------|
| Research Papers | ArXiv (cs.AI, cs.LG, cs.CL, cs.CV) | Official API |
| Code Repositories | GitHub Trending | Web Scraping |
| Company Blogs | OpenAI, HuggingFace | RSS Feed |
| Academic | BAIR (Berkeley) | RSS Feed |
| Personal Blogs | Simon Willison, Sebastian Raschka, Interconnects | RSS Feed |
| Tech Media | MIT Technology Review | RSS Feed |

## Workflow

### 1. Configuration Loading

Load data source configuration from `config/sources.yaml`. Falls back to sensible defaults if not present.

### 2. Parallel Crawling

Execute crawlers for each enabled source:
- **RSS Crawler**: Parse RSS/Atom feeds using `feedparser`
- **ArXiv Crawler**: Query official API using `arxiv` library
- **GitHub Crawler**: Scrape Trending page with `requests` + `BeautifulSoup`

### 3. Data Processing

**Deduplication (2-level)**:
- Level 1: URL MD5 hash deduplication (fastest)
- Level 2: SimHash content fingerprint deduplication

**Classification**: Auto-tag by category (paper/code/blog/discussion/news)

### 4. Report Generation

Generate responsive HTML report with:
- Statistics overview (counts by category)
- Grouped article display
- Original links and summaries
- Tag-based filtering visual

### 5. Output

Save to `/mnt/user-data/outputs/ai-news/ai-news-YYYYMMDD.html`

## Usage

### Command Line

```bash
# Use default configuration
python scripts/crawl.py

# Specify custom config
python scripts/crawl.py --config /path/to/config.yaml

# Custom output directory
python scripts/crawl.py --output-dir ./reports
```

### Python API

```python
from scripts.crawl import run_crawler

# Run with defaults
report_path = run_crawler()

# Custom configuration
report_path = run_crawler(
    config_path="config/sources.yaml",
    output_dir="/custom/output/path"
)
```

## Configuration File

Example `config/sources.yaml`:

```yaml
sources:
  arxiv_ai:
    enabled: true
    config:
      categories: ["cs.AI", "cs.LG", "cs.CL"]
      max_results: 20
      days_back: 3

  github_trending:
    enabled: true
    config:
      languages: ["", "python", "javascript", "rust"]
      since: "daily"  # daily/weekly/monthly

  rss_feeds:
    - name: "OpenAI Blog"
      url: "https://openai.com/news/rss.xml"
      category: "blog"
    - name: "HuggingFace Blog"
      url: "https://huggingface.co/blog/feed.xml"
      category: "blog"

settings:
  request_delay: 1.0  # Seconds between requests
  max_retries: 3
  timeout: 30

deduplication:
  simhash_threshold: 3  # Hamming distance threshold
```

## Project Structure

```
ai-news-crawler/
├── SKILL.md                    # This file
├── scripts/
│   └── crawl.py               # Main entry point script
├── requirements.txt            # Python dependencies
├── config/
│   └── sources.yaml           # Data source configuration
├── assets/
│   └── report_template.html   # Jinja2 HTML template
├── spiders/                   # Crawler modules
│   ├── __init__.py
│   ├── arxiv_spider.py       # ArXiv API crawler
│   ├── github_spider.py      # GitHub Trending scraper
│   └── rss_spider.py         # RSS feed parser
└── processors/               # Data processing modules
    ├── __init__.py
    ├── deduplicator.py      # URL + SimHash deduplication
    └── report_generator.py  # HTML report generation
```

## Quality Checklist

Before delivering the report, verify:

### Data Quality
- [ ] All enabled data sources returned results (or errors were logged)
- [ ] Deduplication removed URL duplicates and content duplicates
- [ ] Article counts match expected totals from each source
- [ ] No articles with empty titles or URLs

### Report Quality
- [ ] HTML renders correctly with proper styling (light/dark mode)
- [ ] All article links are clickable and valid
- [ ] Category badges display correct colors
- [ ] Statistics in header match actual article counts
- [ ] Report includes date and generation timestamp

### Content Verification
- [ ] Articles are properly grouped by category
- [ ] Summaries are truncated appropriately (max 180 chars)
- [ ] Tags display correctly (max 4 per article)
- [ ] Published dates formatted consistently

### Output
- [ ] HTML file saved to specified output directory
- [ ] File naming follows `ai-news-YYYYMMDD.html` format
- [ ] File is accessible at the reported path

## Dependencies

```bash
pip install feedparser arxiv beautifulsoup4 lxml requests jinja2 pyyaml
```

Or use:

```bash
pip install -r requirements.txt
```

## Output Format

The generated HTML report includes:

1. **Header**: Title, date, and statistics cards
2. **Category Sections**: Articles grouped by type
   - 研究论文
   - 开源项目
   - 技术博客
   - 社区讨论
   - 科技资讯
3. **Article Cards**: Title, link, author, date, summary, tags
4. **Responsive Design**: Mobile-friendly layout with dark mode support

## Best Practices

1. **Respect Rate Limits**: Default 1-second delay between requests
2. **Incremental Runs**: The deduplicator prevents duplicates across runs
3. **Customization**: Edit `config/sources.yaml` to add/remove sources
4. **Scheduling**: Set up cron job for daily automated reports

## Troubleshooting

**ArXiv API failures**: Check network connection, API is usually stable
**GitHub scraping fails**: GitHub may block requests; ensure proper User-Agent
**Empty RSS feeds**: Some feeds may be temporarily unavailable

## Extending

To add a new data source:

1. Create spider in `spiders/` directory
2. Implement `crawl()` method returning list of article dicts
3. Add configuration schema to `config/sources.yaml`
4. Import and call in `scripts/crawl.py`

Article dict format:
```python
{
    "source": "Source Name",
    "category": "paper|code|blog|discussion|news",
    "title": "Article Title",
    "url": "https://example.com/article",
    "published": datetime_object or string,
    "summary": "Article summary...",
    "author": "Author Name",
    "tags": ["tag1", "tag2"]
}
```
