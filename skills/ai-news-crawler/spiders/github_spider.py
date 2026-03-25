"""
GitHub Trending crawler - scrape trending repositories
"""
import re
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup


class GitHubCrawler:
    """GitHub Trending crawler"""

    def __init__(self):
        self.base_url = "https://github.com/trending"

    def crawl(
        self,
        languages: List[str] = None,
        since: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Scrape GitHub Trending

        Args:
            languages: List of languages, e.g., ["python", "javascript"]. Empty string for all.
            since: daily/weekly/monthly

        Returns:
            List of repository dictionaries
        """
        if languages is None:
            languages = ["", "python", "javascript"]

        all_repos = []

        for lang in languages:
            repos = self._fetch_language(lang, since)
            all_repos.extend(repos)
            label = f"({lang})" if lang else "(All)"
            print(f"  [GitHub] Trending {label}: {len(repos)} repos")

        return all_repos

    def _fetch_language(self, language: str, since: str) -> List[Dict[str, Any]]:
        """Fetch trending repos for specific language"""
        url = f"{self.base_url}/{language}?since={since}" if language else f"{self.base_url}?since={since}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9"
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            repos = []

            for article in soup.find_all("article", class_="Box-row"):
                try:
                    repo = self._parse_repo(article, language or "All")
                    if repo:
                        repos.append(repo)
                except Exception:
                    continue

            return repos

        except Exception as e:
            print(f"  [GitHub] Error fetching trending: {e}")
            return []

    def _parse_repo(self, article, language: str) -> Dict[str, Any]:
        """Parse single repository info"""
        # Extract repo name
        h2 = article.find("h2", class_="h3 lh-condensed")
        if not h2:
            return None

        repo_link = h2.find("a")
        if not repo_link:
            return None

        repo_text = repo_link.get_text(strip=True)
        repo_name = repo_text.replace(" ", "").replace("\n", "")
        repo_url = f"https://github.com{repo_link['href']}"

        # Extract description
        desc_p = article.find("p", class_="col-9 color-fg-muted my-1 pr-4")
        description = desc_p.get_text(strip=True) if desc_p else ""

        # Extract language
        lang_span = article.find("span", itemprop="programmingLanguage")
        actual_language = lang_span.get_text(strip=True) if lang_span else language

        # Extract stars
        stars = "0"
        stars_link = article.find("a", class_="Link--muted d-inline-block mr-3")
        if stars_link:
            stars_text = stars_link.get_text(strip=True)
            stars = stars_text.replace(",", "").replace("k", "000").replace("K", "000")

        # Extract today's stars
        today_stars = ""
        today_span = article.find("span", class_="d-inline-block float-sm-right")
        if today_span:
            today_stars = today_span.get_text(strip=True).replace(" stars today", "").replace(" star today", "")

        return {
            "source": "GitHub Trending",
            "category": "code",
            "title": f"[GitHub] {repo_name}",
            "url": repo_url,
            "published": None,  # GitHub Trending has no publish time
            "summary": description,
            "author": repo_name.split("/")[0] if "/" in repo_name else "",
            "tags": [actual_language.lower(), "github", "trending"],
            "metadata": {
                "repo_name": repo_name,
                "language": actual_language,
                "stars": stars,
                "stars_today": today_stars
            }
        }
