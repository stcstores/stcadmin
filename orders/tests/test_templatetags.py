import pytest

from orders.templatetags import orders_extras


@pytest.mark.parametrize(
    "price, formatted",
    [
        (522, '<span class="neutral">&pound;5.22</span>'),
        (-522, '<span class="negative">&pound;-5.22</span>'),
        (None, '<span class="negative">&mdash;</span>'),
    ],
)
def test_format_price(price, formatted):
    assert orders_extras.format_price(price) == formatted


@pytest.mark.parametrize(
    "percentage,expected",
    [
        (12, '<span class="success">12%</span>'),
        (11, '<span class="success">11%</span>'),
        (10, '<span class="warning">10%</span>'),
        (1, '<span class="warning">1%</span>'),
        (0, '<span class="error">0%</span>'),
        (-1, '<span class="error">-1%</span>'),
    ],
)
def test_format_percentage(percentage, expected):
    assert orders_extras.format_percentage(percentage) == expected
