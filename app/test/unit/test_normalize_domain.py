import pytest

from app.utils.url_norm import normalize_domain


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("example.ru", "example.ru"),
        ("https://www.example.ru/", "example.ru"),
        ("http://example.ru:443", "example.ru"),
        ("example.ru.", "example.ru"),
        ("", None),
        ("localhost", None),
    ],
)
def test_normalize_domain(raw, expected):
    assert normalize_domain(raw) == expected
