"""
GitHub Trending crawler - scrape trending repositories
"""
import re
import time
import random
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup


class GitHubCrawler:
    """GitHub Trending crawler with retry logic and rate limit handling"""

    def __init__(self, max_retries: int = 3, request_delay: float = 1.0):
        self.base_url = "https://github.com/trending"
        self.max_retries = max_retries
        self.request_delay = request_delay

    def _fetch_with_retry(self, url: str, headers: dict) -> requests.Response:
        """
        Fetch URL with exponential backoff retry logic

        Args:
            url: URL to fetch
            headers: Request headers

        Returns:
            Response object

        Raises:
            requests.RequestException: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    wait_time = retry_after + random.uniform(1, 3)
                    print(f"  [GitHub] Rate limited. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue

                # Check for server errors (5xx) - retry with backoff
                if response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"  [GitHub] Server error {response.status_code}, retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"  [GitHub] Timeout, retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"  [GitHub] Request error: {e}, retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise

        raise requests.RequestException(f"Failed to fetch {url} after {self.max_retries} attempts")

    def crawl(
        self,
        languages: List[str] = None,
        since: str = "daily",
        min_stars: int = 50
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
        """Fetch trending repos for specific language with retry logic"""
        url = f"{self.base_url}/{language}?since={since}" if language else f"{self.base_url}?since={since}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        try:
            response = self._fetch_with_retry(url, headers)

            soup = BeautifulSoup(response.text, "lxml")
            repos = []

            for article in soup.find_all("article", class_="Box-row"):
                try:
                    repo = self._parse_repo(article, language or "All")
                    if repo:
                        repos.append(repo)
                except Exception as e:
                    print(f"  [GitHub] Warning: Failed to parse repo: {e}")
                    continue

            # Respect rate limits with delay
            time.sleep(self.request_delay)

            return repos

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"  [GitHub] Access denied (403). GitHub may be blocking automated requests.")
            else:
                print(f"  [GitHub] HTTP error: {e}")
            return []

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

        # Parse stars number
        def _parse_number(text):
            if not text:
                return 0
            clean = text.replace(",", "").replace(" ", "").lower()
            if "k" in clean:
                return int(float(clean.replace("k", "")) * 1000)
            try:
                return int(clean)
            except:
                return 0

        # Extract stars
        stars = 0
        stars_link = article.find("a", href=re.compile(r"/stargazers$"))
        if stars_link:
            stars = _parse_number(stars_link.get_text(strip=True))

        # Extract forks
        forks = 0
        forks_link = article.find("a", href=re.compile(r"/forks$"))
        if forks_link:
            forks = _parse_number(forks_link.get_text(strip=True))

        # Extract today's stars
        stars_today = 0
        today_span = article.find("span", class_=re.compile(r"float-sm-right"))
        if today_span:
            today_text = today_span.get_text(strip=True)
            # Match pattern like "1,234 stars today" or "5k stars today"
            match = re.search(r"([\d,kK]+)", today_text)
            if match:
                stars_today = _parse_number(match.group(1))

        return {
            "source": "GitHub Trending",
            "category": "code",
            "title": repo_name,
            "url": repo_url,
            "published": None,
            "summary": description,
            "author": repo_name.split("/")[0] if "/" in repo_name else "",
            "tags": [actual_language.lower(), "github", "trending"] if actual_language else ["github", "trending"],
            "language": actual_language,
            "stars": stars,
            "stars_today": stars_today,
            "forks": forks
        }
