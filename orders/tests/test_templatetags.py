from unittest.mock import Mock, patch

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


@patch("orders.templatetags.orders_extras.URLs.order_url")
def test_ccp_order_page(mock_order_url):
    response = Mock()
    mock_order_url.return_value = response
    order_id = "8930983"
    customer_id = "3893094"
    returned_value = orders_extras.ccp_order_page(order_id, customer_id)
    assert returned_value == response
    mock_order_url.assert_called_once_with(
        orders_extras.SUBDOMAIN, order_id, customer_id
    )


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
