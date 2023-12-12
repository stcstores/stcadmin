import pytest
from django.utils.safestring import SafeString

from fba.templatetags.fba_extras import format_price


def test_returns_safe_string():
    assert isinstance(format_price(500), SafeString)


@pytest.mark.parametrize(
    "value,expected",
    (
        (None, '<span class="text-danger">&mdash;</span>'),
        (500, '<span class="text-dark">&pound;5.00</span>'),
        (1855, '<span class="text-dark">&pound;18.55</span>'),
        (1, '<span class="text-dark">&pound;0.01</span>'),
        (-205, '<span class="text-danger">&pound;-2.05</span>'),
    ),
)
def test_format_price_return_value(value, expected):
    assert format_price(value) == expected
