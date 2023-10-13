from unittest import mock

import pytest

from restock import views


@pytest.fixture
def product():
    return mock.Mock()


@mock.patch("restock.views.FBAOrder")
@mock.patch("restock.views.models.Reorder")
def test_add_details_to_product_adds_fba_order_count(
    mock_reorder, mock_fba_order, product
):
    views.add_details_to_product(product)
    mock_fba_order.objects.awaiting_fulfillment.return_value.filter.assert_called_once_with(
        product=product
    )
    mock_fba_order.objects.awaiting_fulfillment.return_value.filter.return_value.count.assert_called_once_with()
    order_count = (
        mock_fba_order.objects.awaiting_fulfillment.return_value.filter.return_value.count.return_value
    )
    assert product.fba_order_count == order_count


@mock.patch("restock.views.FBAOrder")
@mock.patch("restock.views.models.Reorder")
def test_add_details_to_product_adds_last_reorder(
    mock_reorder, mock_fba_order, product
):
    views.add_details_to_product(product)
    mock_reorder.objects.last_reorder.assert_called_once_with(product)
    assert product.last_reorder == mock_reorder.objects.last_reorder.return_value
