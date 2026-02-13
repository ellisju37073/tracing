"""Tests for HTML parser."""

import pytest
from src.parser import HTMLParser


@pytest.fixture
def parser():
    return HTMLParser()


@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page for scraping">
    </head>
    <body>
        <h1>Main Heading</h1>
        <h2>Subheading 1</h2>
        <h2>Subheading 2</h2>
        <p>Some content here.</p>
        <a href="https://example.com">Example Link</a>
        <a href="/about">About Page</a>
    </body>
    </html>
    """


def test_parse_extracts_title(parser, sample_html):
    result = parser.parse(sample_html)
    assert result["title"] == "Test Page"


def test_parse_extracts_meta_description(parser, sample_html):
    result = parser.parse(sample_html)
    assert result["meta_description"] == "A test page for scraping"


def test_parse_extracts_links(parser, sample_html):
    result = parser.parse(sample_html)
    assert len(result["links"]) == 2
    assert result["links"][0]["href"] == "https://example.com"
    assert result["links"][0]["text"] == "Example Link"


def test_parse_extracts_headings(parser, sample_html):
    result = parser.parse(sample_html)
    assert "h1" in result["headings"]
    assert "h2" in result["headings"]
    assert result["headings"]["h1"] == ["Main Heading"]
    assert len(result["headings"]["h2"]) == 2


def test_select_returns_text(parser, sample_html):
    result = parser.select(sample_html, "h2")
    assert result == ["Subheading 1", "Subheading 2"]


def test_select_attrs_returns_attribute_values(parser, sample_html):
    result = parser.select_attrs(sample_html, "a", "href")
    assert "https://example.com" in result
    assert "/about" in result
