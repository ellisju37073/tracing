"""Helper utility functions."""

import re
from urllib.parse import urljoin, urlparse
from typing import Optional


def clean_text(text: str) -> str:
    """Clean and normalize text content.

    Args:
        text: Raw text to clean.

    Returns:
        Cleaned text with normalized whitespace.
    """
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Normalize a URL, optionally resolving relative URLs.

    Args:
        url: The URL to normalize.
        base_url: Optional base URL for resolving relative URLs.

    Returns:
        Normalized absolute URL.
    """
    # Remove leading/trailing whitespace
    url = url.strip()

    # Resolve relative URLs
    if base_url and not url.startswith(("http://", "https://", "//")):
        url = urljoin(base_url, url)

    # Handle protocol-relative URLs
    if url.startswith("//"):
        url = "https:" + url

    return url


def extract_domain(url: str) -> str:
    """Extract the domain from a URL.

    Args:
        url: The URL to extract domain from.

    Returns:
        The domain name.
    """
    parsed = urlparse(url)
    return parsed.netloc


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: The string to check.

    Returns:
        True if valid URL, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_file_extension(url: str) -> Optional[str]:
    """Extract file extension from URL path.

    Args:
        url: The URL to extract extension from.

    Returns:
        The file extension (without dot), or None if not found.
    """
    parsed = urlparse(url)
    path = parsed.path
    if "." in path:
        return path.rsplit(".", 1)[-1].lower()
    return None
