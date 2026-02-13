# Web Scraper

A Python-based web scraping library with modular architecture for scraping, parsing, and data storage.

## Features

- **Async HTTP Client**: Built on `httpx` for fast, async HTTP requests
- **Concurrent Scraping**: Support for rate-limited concurrent requests
- **HTML Parsing**: BeautifulSoup with lxml backend for fast parsing
- **Flexible Storage**: JSON and CSV storage handlers
- **Utility Functions**: URL normalization, text cleaning, rate limiting

## Project Structure

```
├── src/
│   ├── scraper/       # Web scraping modules
│   │   ├── base.py    # Base scraper with httpx
│   │   └── async_scraper.py  # Concurrent scraping
│   ├── parser/        # HTML parsing utilities
│   │   ├── html_parser.py    # BeautifulSoup wrapper
│   │   └── selectors.py      # Common CSS selectors
│   ├── storage/       # Data storage handlers
│   │   ├── json_storage.py   # JSON file storage
│   │   └── csv_storage.py    # CSV file storage
│   └── utils/         # Common utilities
│       ├── helpers.py        # Helper functions
│       └── rate_limiter.py   # Rate limiting
├── tests/             # Test files
├── data/              # Output data directory
└── requirements.txt   # Dependencies
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Quick Start

```python
import asyncio
from src.scraper import WebScraper
from src.parser import HTMLParser
from src.storage import JSONStorage

async def main():
    scraper = WebScraper()
    parser = HTMLParser()
    storage = JSONStorage("data/output.json")

    # Fetch a page
    html = await scraper.fetch("https://example.com")
    
    # Parse the HTML
    data = parser.parse(html)
    
    # Save the data
    storage.save(data)
    
    await scraper.close()

asyncio.run(main())
```

## Concurrent Scraping

```python
from src.scraper import AsyncScraper

async def scrape_multiple():
    scraper = AsyncScraper(max_concurrent=5, delay=0.5)
    
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]
    
    results = await scraper.fetch_all(urls)
    await scraper.close()
    return results
```

## Custom Parsing

```python
from src.parser import HTMLParser

parser = HTMLParser()

# Use CSS selectors
titles = parser.select(html, "h1.title")
links = parser.select_attrs(html, "a.nav-link", "href")

# Get BeautifulSoup object for complex parsing
soup = parser.get_soup(html)
custom_data = soup.find_all("div", class_="product")
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_parser.py
```

## Development

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src
```

