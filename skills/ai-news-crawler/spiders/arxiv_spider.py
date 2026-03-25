"""
ArXiv paper crawler using the official arxiv library
"""
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Any


class ArXivCrawler:
    """ArXiv paper crawler"""

    def __init__(self):
        self.client = arxiv.Client()

    def crawl(
        self,
        categories: List[str] = None,
        max_results: int = 20,
        days_back: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Fetch latest papers from ArXiv

        Args:
            categories: List of paper categories, e.g., ["cs.AI", "cs.LG"]
            max_results: Maximum results per category
            days_back: Only fetch papers from last N days

        Returns:
            List of paper dictionaries
        """
        if categories is None:
            categories = ["cs.AI", "cs.LG", "cs.CL"]

        all_papers = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for category in categories:
            print(f"  [ArXiv] Fetching {category}...")

            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )

            for result in self.client.results(search):
                # Only get recent papers
                if result.published < cutoff_date:
                    break

                paper = {
                    "source": f"ArXiv {category}",
                    "category": "paper",
                    "title": result.title,
                    "url": result.pdf_url or result.entry_id,
                    "published": result.published,
                    "summary": result.summary[:500] + "..." if len(result.summary) > 500 else result.summary,
                    "author": ", ".join([str(a) for a in result.authors[:3]]),
                    "tags": list(result.categories) + ["paper", "arxiv"],
                    "metadata": {
                        "arxiv_id": result.entry_id.split('/')[-1],
                        "primary_category": result.primary_category,
                        "comment": result.comment or ""
                    }
                }
                all_papers.append(paper)

        # Sort by date
        all_papers.sort(key=lambda x: x["published"], reverse=True)

        print(f"  [ArXiv] Fetched {len(all_papers)} papers")
        return all_papers

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search ArXiv papers

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of paper dictionaries
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for result in self.client.results(search):
            papers.append({
                "source": "ArXiv Search",
                "category": "paper",
                "title": result.title,
                "url": result.pdf_url or result.entry_id,
                "published": result.published,
                "summary": result.summary[:300] + "..." if len(result.summary) > 300 else result.summary,
                "author": ", ".join([str(a) for a in result.authors[:3]]),
                "tags": list(result.categories) + ["paper"]
            })

        return papers
