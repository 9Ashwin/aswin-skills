"""
HTML report generator - Developer focused with code highlighting
"""
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict, Counter

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ReportGenerator:
    """HTML daily report generator for developers"""

    def __init__(self, template_dir: str = None):
        """
        Initialize generator

        Args:
            template_dir: Template directory path, defaults to ../templates relative to this file
        """
        if template_dir is None:
            template_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets"
            )

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.template = self.env.get_template("report_template.html")

    def _group_by_source(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group articles by source"""
        groups = defaultdict(list)
        for item in items:
            source = item.get("source", "Other")
            groups[source].append(item)
        return dict(groups)

    def _calculate_stats(self, articles: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for the report"""
        total = len(articles)

        # Count unique sources
        sources = Counter([a.get("source", "Unknown") for a in articles])
        source_count = len(sources)

        # Count by category
        categories = Counter([a.get("dev_category", "other") for a in articles])

        # GitHub stats
        github_items = [a for a in articles if a.get("dev_category") == "code"]
        total_stars = sum(a.get("stars", 0) for a in github_items)
        total_new_stars = sum(a.get("stars_today", 0) for a in github_items)

        # Top languages
        languages = Counter([a.get("language", "Unknown") for a in github_items if a.get("language")]).most_common(5)

        # Paper stats
        paper_items = [a for a in articles if a.get("dev_category") == "paper"]
        paper_categories = Counter([a.get("source", "").replace("ArXiv ", "") for a in paper_items]).most_common(3)

        return {
            "total": total,
            "source_count": source_count,
            "top_sources": sources.most_common(5),
            "categories": dict(categories),
            "github_count": len(github_items),
            "total_stars": total_stars,
            "total_new_stars": total_new_stars,
            "top_languages": languages,
            "papers_count": len(paper_items),
            "top_paper_categories": paper_categories
        }

    def generate(
        self,
        articles: List[Dict[str, Any]],
        report_date: datetime = None,
        overall_summary: str = None,
        category_summaries: Dict[str, str] = None,
        key_takeaways: List[str] = None,
        include_code_snippets: bool = True
    ) -> str:
        """
        Generate HTML daily report with developer-focused categories

        Args:
            articles: List of article dictionaries
            report_date: Report date
            overall_summary: AI-generated overall summary
            category_summaries: Dict with category summaries
            key_takeaways: List of key takeaway strings
            include_code_snippets: Whether to include code snippets

        Returns:
            HTML string
        """
        if report_date is None:
            report_date = datetime.now()

        # Group by dev_category
        llm_items = [a for a in articles if a.get("dev_category") == "llm"]
        paper_items = [a for a in articles if a.get("dev_category") == "paper"]
        code_items = [a for a in articles if a.get("dev_category") == "code"]
        tool_items = [a for a in articles if a.get("dev_category") == "tool"]
        infra_items = [a for a in articles if a.get("dev_category") == "infra"]
        tutorial_items = [a for a in articles if a.get("dev_category") == "tutorial"]

        # Sort by published date if available
        for items in [llm_items, paper_items, code_items, tool_items, infra_items, tutorial_items]:
            try:
                items.sort(key=lambda x: x.get("published") or datetime.min, reverse=True)
            except:
                pass

        # Group by source for each category
        llm_by_source = self._group_by_source(llm_items)
        papers_by_source = self._group_by_source(paper_items)
        code_by_source = self._group_by_source(code_items)
        tool_by_source = self._group_by_source(tool_items)
        infra_by_source = self._group_by_source(infra_items)
        tutorial_by_source = self._group_by_source(tutorial_items)

        # Calculate stats
        stats = self._calculate_stats(articles)

        category_summaries = category_summaries or {}
        key_takeaways = key_takeaways or []

        html = self.template.render(
            # Category items
            llm_items=llm_items,
            paper_items=paper_items,
            code_items=code_items,
            tool_items=tool_items,
            infra_items=infra_items,
            tutorial_items=tutorial_items,
            # Source groupings
            llm_by_source=llm_by_source,
            papers_by_source=papers_by_source,
            code_by_source=code_by_source,
            tool_by_source=tool_by_source,
            infra_by_source=infra_by_source,
            tutorial_by_source=tutorial_by_source,
            # Counts
            llm_count=len(llm_items),
            papers_count=len(paper_items),
            code_count=len(code_items),
            tool_count=len(tool_items),
            infra_count=len(infra_items),
            tutorial_count=len(tutorial_items),
            total_count=len(articles),
            # Stats
            stats=stats,
            # Key takeaways
            key_takeaways=key_takeaways,
            # Metadata
            report_date=report_date,
            overall_summary=overall_summary,
            llm_summary=category_summaries.get("llm"),
            papers_summary=category_summaries.get("papers"),
            code_summary=category_summaries.get("code"),
            tool_summary=category_summaries.get("tool"),
            infra_summary=category_summaries.get("infra"),
            tutorial_summary=category_summaries.get("tutorial"),
            include_code_snippets=include_code_snippets
        )

        return html

    def save(self, html: str, output_path: str):
        """Save HTML file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  [Report] Saved to: {output_path}")
