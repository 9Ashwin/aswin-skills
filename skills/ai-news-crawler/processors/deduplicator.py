"""
Content deduplication processor - URL and SimHash based
"""
import hashlib
from typing import Set, List, Dict, Any
from datetime import datetime


class Deduplicator:
    """
    Multi-level deduplicator

    Level 1: URL MD5 deduplication (fastest)
    Level 2: SimHash content fingerprint deduplication
    """

    def __init__(self, simhash_threshold: int = 3):
        self.url_hashes: Set[str] = set()
        self.content_hashes: Set[int] = set()
        self.simhash_threshold = simhash_threshold

    def is_duplicate_url(self, url: str) -> bool:
        """Check if URL already exists"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.url_hashes:
            return True
        self.url_hashes.add(url_hash)
        return False

    def is_duplicate_content(self, content: str) -> bool:
        """Check if content is duplicate using SimHash"""
        content_hash = self._simhash(content)

        for existing_hash in self.content_hashes:
            if self._hamming_distance(content_hash, existing_hash) <= self.simhash_threshold:
                return True

        self.content_hashes.add(content_hash)
        return False

    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate article list

        Returns:
            Deduplicated article list
        """
        unique_articles = []
        duplicates_count = {"url": 0, "content": 0}

        for article in articles:
            # URL deduplication
            if self.is_duplicate_url(article.get("url", "")):
                duplicates_count["url"] += 1
                continue

            # Content deduplication
            content = article.get("summary", "") + article.get("title", "")
            if content and self.is_duplicate_content(content):
                duplicates_count["content"] += 1
                continue

            unique_articles.append(article)

        print(f"  [Deduplicate] URL duplicates: {duplicates_count['url']}, Content duplicates: {duplicates_count['content']}")
        print(f"  [Deduplicate] Kept {len(unique_articles)} unique articles")

        return unique_articles

    def _simhash(self, text: str) -> int:
        """
        Calculate SimHash fingerprint (simplified version)

        For production, consider using the simhash library
        """
        # Simple feature extraction
        words = text.lower().split()

        # Weighted hash
        hashes = []
        for word in words[:100]:  # Limit length
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
            hashes.append(hash_val)

        if not hashes:
            return 0

        # Merge using XOR
        result = 0
        for h in hashes:
            result ^= h

        return result & 0xFFFFFFFFFFFFFFFF  # 64-bit

    def _hamming_distance(self, hash1: int, hash2: int) -> int:
        """Calculate Hamming distance"""
        x = hash1 ^ hash2
        distance = 0
        while x:
            distance += 1
            x &= x - 1
        return distance
