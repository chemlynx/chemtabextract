"""Regression tests for URL validation in chemtabextract.input.from_any.

Ensures the stdlib urllib.parse replacement for the former Django URLValidator
accepts and rejects the same URL forms that the library needs to distinguish.
"""

import pytest

from chemtabextract.input.from_any import url


@pytest.mark.parametrize(
    "value,expected",
    [
        # --- valid URLs ---
        ("http://example.com/table.html", True),
        ("https://example.com/table.html", True),
        ("ftp://example.com/table.csv", True),
        # private IP — accepted; SSRF prevention is caller's responsibility
        ("http://192.168.1.1/table.html", True),
        ("https://10.0.0.1/data.html", True),
        # --- invalid / non-URL strings ---
        ("example.com/table.html", False),  # missing scheme
        ("not-a-url", False),
        ("", False),
        ("/local/path/table.csv", False),  # local path, no scheme
        ("file:///etc/passwd", False),  # file:// scheme not in whitelist
        ("mailto:user@example.com", False),  # mailto:// scheme not in whitelist
    ],
)
def test_url_detection(value: str, expected: bool) -> None:
    """url() returns the correct boolean for each input."""
    assert url(value) == expected
