"""
ArXiv paper crawler - Developer focused with code link extraction
"""
import re
import time
import random
import arxiv
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any


class ArXivCrawler:
    """ArXiv paper crawler with tech-focused extraction and retry logic"""

    def __init__(self, max_retries: int = 3, request_delay: float = 1.0):
        self.client = arxiv.Client(
            num_retries=max_retries,
            delay_seconds=request_delay
        )
        self.max_retries = max_retries
        self.request_delay = request_delay

    def crawl(
        self,
        categories: List[str] = None,
        max_results: int = 20,
        days_back: int = 3,
        fetch_code_links: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch latest papers from ArXiv with developer-focused metadata

        Args:
            categories: List of paper categories
            max_results: Maximum results per category
            days_back: Only fetch papers from last N days
            fetch_code_links: Extract GitHub/code links from paper

        Returns:
            List of paper dictionaries with tech metadata
        """
        if categories is None:
            categories = ["cs.AI", "cs.LG", "cs.CL", "cs.SE", "cs.SY"]

        all_papers = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        for category in categories:
            print(f"  [ArXiv] Fetching {category}...")

            for attempt in range(self.max_retries):
                try:
                    search = arxiv.Search(
                        query=f"cat:{category}",
                        max_results=max_results,
                        sort_by=arxiv.SortCriterion.SubmittedDate
                    )

                    category_papers = []
                    for result in self.client.results(search):
                        if result.published < cutoff_date:
                            break

                        # Extract technical highlights
                        tech_highlights = self._extract_tech_highlights(result.summary)

                        # Extract code links
                        code_links = []
                        if fetch_code_links:
                            code_links = self._extract_code_links(result.summary)

                        # Assess complexity
                        complexity = self._assess_complexity(result.summary, result.categories)

                        paper = {
                            "source": f"ArXiv {category}",
                            "category": "paper",
                            "dev_category": "paper",
                            "title": result.title,
                            "url": result.pdf_url or result.entry_id,
                            "published": result.published,
                            "summary": result.summary[:500] + "..." if len(result.summary) > 500 else result.summary,
                            "author": ", ".join([str(a) for a in result.authors[:3]]),
                            "tags": list(result.categories) + ["paper", "arxiv"],
                            "metadata": {
                                "arxiv_id": result.entry_id.split('/')[-1],
                                "primary_category": result.primary_category,
                                "comment": result.comment or "",
                                "tech_highlights": tech_highlights,
                                "code_links": code_links,
                                "complexity": complexity,
                                "applicability": self._assess_applicability(result.summary, code_links)
                            }
                        }
                        category_papers.append(paper)

                    all_papers.extend(category_papers)
                    break  # Success, exit retry loop

                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"  [ArXiv] Error fetching {category}: {e}, retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"  [ArXiv] Failed to fetch {category} after {self.max_retries} attempts: {e}")

            # Respect rate limits between categories
            time.sleep(self.request_delay)

        all_papers.sort(key=lambda x: x["published"], reverse=True)
        print(f"  [ArXiv] Fetched {len(all_papers)} papers")
        return all_papers

    def _extract_tech_highlights(self, summary: str) -> List[str]:
        """Extract technical highlights from paper summary"""
        highlights = []
        text = summary.lower()

        # Performance improvements
        perf_patterns = [
            r'(\d+)x\s+faster',
            r'(\d+)%\s+(?:better|improvement|higher)',
            r'speedup\s+of\s+(\d+)',
            r'reduces?\s+latency\s+by\s+(\d+)',
            r'outperforms?\s+.*?by\s+(\d+)'
        ]
        for pattern in perf_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                highlights.append(f"性能: {m}x 提升" if 'x' in pattern else f"性能: {m}% 提升")

        # Architecture innovations
        arch_keywords = [
            "transformer", "attention", "moe", "mixture of experts",
            "diffusion", "gan", "vae", "flow-based", "state space",
            "mamba", "retnet", "rwkv", "mamba"
        ]
        for kw in arch_keywords:
            if kw in text:
                highlights.append(f"架构: {kw.upper()}")

        # Scale
        scale_patterns = [
            r'(\d+)\s*(?:billion|b)\s+parameters',
            r'(\d+)\s*(?:million|m)\s+parameters',
            r'trained\s+on\s+(\d+)\s*(?:billion|b)\s+tokens',
            r'(\d+)\s*(?:billion|b)\s+images',
        ]
        for pattern in scale_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                highlights.append(f"规模: {m}")

        # Capabilities
        capability_keywords = [
            "multimodal", "vision-language", "code generation",
            "reasoning", "long-context", "few-shot", "zero-shot",
            "instruction-tuned", "rlhf", "chain-of-thought"
        ]
        for kw in capability_keywords:
            if kw in text:
                highlights.append(f"能力: {kw}")

        return list(set(highlights))[:5]  # Max 5 highlights

    def _extract_code_links(self, summary: str) -> List[Dict[str, str]]:
        """Extract code repository links from paper"""
        links = []

        # GitHub links
        github_pattern = r'https?://github\.com/[\w\-]+/[\w\-\.]+'
        github_matches = re.findall(github_pattern, summary)
        for url in github_matches:
            links.append({"type": "github", "url": url})

        # Other code repos
        other_patterns = {
            "huggingface": r'https?://huggingface\.co/[\w\-]+/[\w\-\.]+',
            "gitlab": r'https?://gitlab\.com/[\w\-]+/[\w\-\.]+',
            "bitbucket": r'https?://bitbucket\.org/[\w\-]+/[\w\-\.]+',
        }
        for repo_type, pattern in other_patterns.items():
            matches = re.findall(pattern, summary)
            for url in matches:
                links.append({"type": repo_type, "url": url})

        return links

    def _assess_complexity(self, summary: str, categories: List[str]) -> str:
        """Assess paper complexity for developers"""
        text = summary.lower()

        # High complexity indicators
        high_indicators = [
            "theorem", "proof", "convergence", "gradient flow",
            "variational", "differential equation", "manifold",
            "information theory", "statistical mechanics"
        ]
        if any(ind in text for ind in high_indicators):
            return "高阶"

        # Low complexity (accessible)
        low_indicators = [
            "empirical study", "case study", "benchmark",
            "dataset", "survey", "review"
        ]
        if any(ind in text for ind in low_indicators):
            return "入门"

        return "中等"

    def _assess_applicability(self, summary: str, code_links: List[Dict]) -> str:
        """Assess how applicable the paper is for production use"""
        text = summary.lower()

        # Production ready indicators
        production_indicators = [
            "open source", "source code", "github", "available",
            "deployment", "inference", "efficient"
        ]
        score = sum(1 for ind in production_indicators if ind in text)
        score += len(code_links) * 2

        if score >= 3:
            return "可直接用于生产"
        elif score >= 1:
            return "有实现潜力"
        else:
            return "理论研究"

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search ArXiv papers"""
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
                "dev_category": "paper",
                "title": result.title,
                "url": result.pdf_url or result.entry_id,
                "published": result.published,
                "summary": result.summary[:300] + "..." if len(result.summary) > 300 else result.summary,
                "author": ", ".join([str(a) for a in result.authors[:3]]),
                "tags": list(result.categories) + ["paper"],
                "metadata": {
                    "complexity": self._assess_complexity(result.summary, result.categories),
                    "applicability": self._assess_applicability(result.summary, [])
                }
            })

        return papers
