"""Async scraper with concurrent request support."""

import asyncio
from typing import List, Optional, Dict, Any
from .base import WebScraper


class AsyncScraper(WebScraper):
    """Async scraper with support for concurrent requests."""

    def __init__(
        self,
        max_concurrent: int = 5,
        delay: float = 0.5,
        **kwargs,
    ):
        """Initialize the async scraper.

        Args:
            max_concurrent: Maximum number of concurrent requests.
            delay: Delay between requests in seconds.
            **kwargs: Additional arguments for WebScraper.
        """
        super().__init__(**kwargs)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay

    async def fetch_with_limit(self, url: str) -> Optional[str]:
        """Fetch a URL with rate limiting.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content, or None if the request failed.
        """
        async with self.semaphore:
            result = await self.fetch(url)
            await asyncio.sleep(self.delay)
            return result

    async def fetch_all(self, urls: List[str]) -> List[Optional[str]]:
        """Fetch multiple URLs concurrently.

        Args:
            urls: List of URLs to fetch.

        Returns:
            List of HTML content strings (or None for failed requests).
        """
        tasks = [self.fetch_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def fetch_all_json(self, urls: List[str]) -> List[Optional[Dict[str, Any]]]:
        """Fetch multiple URLs and parse as JSON.

        Args:
            urls: List of URLs to fetch.

        Returns:
            List of JSON dictionaries (or None for failed requests).
        """
        async def fetch_json_with_limit(url: str):
            async with self.semaphore:
                result = await self.fetch_json(url)
                await asyncio.sleep(self.delay)
                return result

        tasks = [fetch_json_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)
