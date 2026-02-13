"""Tests for utility functions."""

import pytest
from src.utils.helpers import (
    clean_text,
    normalize_url,
    extract_domain,
    is_valid_url,
    get_file_extension,
)


class TestCleanText:
    def test_removes_extra_whitespace(self):
        assert clean_text("hello   world") == "hello world"

    def test_removes_newlines(self):
        assert clean_text("hello\n\nworld") == "hello world"

    def test_strips_leading_trailing(self):
        assert clean_text("  hello  ") == "hello"


class TestNormalizeUrl:
    def test_absolute_url_unchanged(self):
        url = "https://example.com/page"
        assert normalize_url(url) == url

    def test_resolves_relative_url(self):
        result = normalize_url("/page", base_url="https://example.com")
        assert result == "https://example.com/page"

    def test_handles_protocol_relative(self):
        assert normalize_url("//example.com/page") == "https://example.com/page"


class TestExtractDomain:
    def test_extracts_domain(self):
        assert extract_domain("https://example.com/page") == "example.com"

    def test_includes_subdomain(self):
        assert extract_domain("https://www.example.com") == "www.example.com"


class TestIsValidUrl:
    def test_valid_http_url(self):
        assert is_valid_url("http://example.com")

    def test_valid_https_url(self):
        assert is_valid_url("https://example.com/path?query=1")

    def test_invalid_url(self):
        assert not is_valid_url("not a url")

    def test_missing_scheme(self):
        assert not is_valid_url("example.com")


class TestGetFileExtension:
    def test_extracts_extension(self):
        assert get_file_extension("https://example.com/file.pdf") == "pdf"

    def test_handles_no_extension(self):
        assert get_file_extension("https://example.com/page") is None

    def test_lowercase_extension(self):
        assert get_file_extension("https://example.com/file.PDF") == "pdf"
