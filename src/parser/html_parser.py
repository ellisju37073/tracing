"""HTML parser using BeautifulSoup."""

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional


class HTMLParser:
    """HTML parser using BeautifulSoup with lxml backend."""

    def __init__(self, parser: str = "lxml"):
        """Initialize the parser.

        Args:
            parser: The parser backend to use (lxml, html.parser, etc.)
        """
        self.parser = parser

    def parse(self, html: str) -> Dict[str, Any]:
        """Parse HTML and extract basic information.

        Args:
            html: The HTML content to parse.

        Returns:
            Dictionary containing extracted data.
        """
        soup = BeautifulSoup(html, self.parser)

        return {
            "title": self.get_title(soup),
            "meta_description": self.get_meta_description(soup),
            "links": self.get_links(soup),
            "headings": self.get_headings(soup),
        }

    def get_soup(self, html: str) -> BeautifulSoup:
        """Get a BeautifulSoup object for custom parsing.

        Args:
            html: The HTML content.

        Returns:
            BeautifulSoup object.
        """
        return BeautifulSoup(html, self.parser)

    def get_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the page title.

        Args:
            soup: BeautifulSoup object.

        Returns:
            The page title, or None if not found.
        """
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else None

    def get_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the meta description.

        Args:
            soup: BeautifulSoup object.

        Returns:
            The meta description, or None if not found.
        """
        meta = soup.find("meta", attrs={"name": "description"})
        return meta.get("content") if meta else None

    def get_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links from the page.

        Args:
            soup: BeautifulSoup object.

        Returns:
            List of dictionaries containing link href and text.
        """
        links = []
        for a_tag in soup.find_all("a", href=True):
            links.append({
                "href": a_tag["href"],
                "text": a_tag.get_text(strip=True),
            })
        return links

    def get_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings (h1-h6) from the page.

        Args:
            soup: BeautifulSoup object.

        Returns:
            Dictionary mapping heading levels to lists of heading texts.
        """
        headings = {}
        for level in range(1, 7):
            tag_name = f"h{level}"
            found = soup.find_all(tag_name)
            if found:
                headings[tag_name] = [h.get_text(strip=True) for h in found]
        return headings

    def select(self, html: str, selector: str) -> List[str]:
        """Select elements using CSS selector.

        Args:
            html: The HTML content.
            selector: CSS selector string.

        Returns:
            List of text content from matching elements.
        """
        soup = self.get_soup(html)
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements]

    def select_attrs(
        self, html: str, selector: str, attr: str
    ) -> List[Optional[str]]:
        """Select element attributes using CSS selector.

        Args:
            html: The HTML content.
            selector: CSS selector string.
            attr: Attribute name to extract.

        Returns:
            List of attribute values from matching elements.
        """
        soup = self.get_soup(html)
        elements = soup.select(selector)
        return [el.get(attr) for el in elements]
