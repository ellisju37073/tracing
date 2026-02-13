"""Main entry point for the web scraper."""

import asyncio
from src.scraper import WebScraper
from src.parser import HTMLParser
from src.storage import JSONStorage


async def main():
    """Run the web scraper."""
    # Example usage
    scraper = WebScraper()
    parser = HTMLParser()
    storage = JSONStorage("data/output.json")

    # Example: Scrape a webpage
    url = "https://example.com"
    print(f"Scraping {url}...")

    html = await scraper.fetch(url)
    if html:
        data = parser.parse(html)
        storage.save(data)
        print(f"Data saved to {storage.filepath}")
    else:
        print("Failed to fetch the page")

    await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
