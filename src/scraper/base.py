"""Base web scraper using httpx."""

import httpx
from typing import Optional, Dict, Any


class WebScraper:
    """A simple web scraper using httpx for async HTTP requests."""

    def __init__(
        self,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """Initialize the scraper.

        Args:
            headers: Custom headers to send with requests.
            timeout: Request timeout in seconds.
        """
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (compatible; WebScraper/1.0)"
        }
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return the HTML content.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content as a string, or None if the request failed.
        """
        try:
            client = await self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"HTTP error fetching {url}: {e}")
            return None

    async def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a URL and return JSON data.

        Args:
            url: The URL to fetch.

        Returns:
            The JSON data as a dictionary, or None if the request failed.
        """
        try:
            client = await self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error fetching {url}: {e}")
            return None

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
