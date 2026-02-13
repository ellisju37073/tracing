# Web Scraper Project

A Python-based web scraping project with modular architecture for scraping, parsing, and data storage.

## Project Structure

- `src/` - Main source code
  - `scraper/` - Web scraping modules
  - `parser/` - HTML parsing utilities
  - `storage/` - Data storage handlers
  - `utils/` - Common utilities
- `tests/` - Test files
- `data/` - Output data directory

## Dependencies

- `requests` - HTTP requests
- `httpx` - Async HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser
- `aiohttp` - Async HTTP

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python -m src.main
```

## Development

- Use virtual environment: `python -m venv venv`
- Activate: `source venv/bin/activate`
- Install dev dependencies: `pip install -r requirements-dev.txt`
