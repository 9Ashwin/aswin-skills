"""
HTML report generator - uses Jinja2 templates
"""
import os
from datetime import datetime
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ReportGenerator:
    """HTML daily report generator"""

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

    def generate(
        self,
        articles: List[Dict[str, Any]],
        report_date: datetime = None,
        summary: str = None
    ) -> str:
        """
        Generate HTML daily report

        Args:
            articles: List of article dictionaries
            report_date: Report date
            summary: AI-generated summary of trends (optional)

        Returns:
            HTML string
        """
        if report_date is None:
            report_date = datetime.now()

        grouped = self._group_by_category(articles)
        stats = self._calc_stats(articles)

        html = self.template.render(
            grouped=grouped,
            stats=stats,
            report_date=report_date,
            summary=summary
        )

        return html

    def _group_by_category(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group articles by category"""
        groups = {
            "研究论文": [],
            "开源项目": [],
            "技术博客": [],
            "社区讨论": [],
            "科技资讯": [],
            "其他": []
        }

        for article in articles:
            cat = article.get("category", "other")

            if cat == "paper":
                groups["研究论文"].append(article)
            elif cat == "code":
                groups["开源项目"].append(article)
            elif cat == "blog":
                groups["技术博客"].append(article)
            elif cat == "discussion":
                groups["社区讨论"].append(article)
            elif cat == "news":
                groups["科技资讯"].append(article)
            else:
                groups["其他"].append(article)

        # Filter empty categories
        return {k: v for k, v in groups.items() if v}

    def _calc_stats(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate statistics"""
        return {
            "total": len(articles),
            "paper": len([a for a in articles if a.get("category") == "paper"]),
            "code": len([a for a in articles if a.get("category") == "code"]),
            "blog": len([a for a in articles if a.get("category") == "blog"]),
            "discussion": len([a for a in articles if a.get("category") == "discussion"]),
            "news": len([a for a in articles if a.get("category") == "news"])
        }

    def save(self, html: str, output_path: str):
        """Save HTML file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  [Report] Saved to: {output_path}")
