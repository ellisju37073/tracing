"""Rate limiting utilities."""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """Rate limiter for controlling request frequency."""

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst: int = 1,
    ):
        """Initialize the rate limiter.

        Args:
            requests_per_second: Maximum requests per second.
            burst: Maximum burst size (requests allowed at once).
        """
        self.rate = requests_per_second
        self.burst = burst
        self.tokens = burst
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request.

        This method will wait if necessary to respect the rate limit.
        """
        async with self._lock:
            await self._wait_for_token()

    async def _wait_for_token(self) -> None:
        """Wait until a token is available."""
        while True:
            self._refill_tokens()
            if self.tokens >= 1:
                self.tokens -= 1
                return
            # Calculate wait time
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update
        self.last_update = now

        # Add tokens based on elapsed time
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)

    async def __aenter__(self) -> "RateLimiter":
        """Async context manager entry."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        pass


class SyncRateLimiter:
    """Synchronous rate limiter for non-async code."""

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst: int = 1,
    ):
        """Initialize the synchronous rate limiter.

        Args:
            requests_per_second: Maximum requests per second.
            burst: Maximum burst size.
        """
        self.interval = 1.0 / requests_per_second
        self.last_request: Optional[float] = None

    def wait(self) -> None:
        """Wait if necessary to respect the rate limit."""
        if self.last_request is not None:
            elapsed = time.monotonic() - self.last_request
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)
        self.last_request = time.monotonic()

    def __enter__(self) -> "SyncRateLimiter":
        """Context manager entry."""
        self.wait()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        pass
