from unittest import mock

import pytest

from channels.models.shopify_models.shopify_manager import (
    ShopifyManager,
    ShopifyStockManager,
)


@pytest.fixture
def mock_shopify_manager():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyManager"
    ) as m:
        yield m


@pytest.fixture
def mock_get_products():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyStockManager._get_products"
    ) as m:
        yield m


@pytest.fixture
def mock_update_product_status():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyStockManager._update_product_status"
    ) as m:
        yield m


@pytest.fixture
def mock_get_stock_level():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyStockManager._get_stock_level"
    ) as m:
        yield m


@pytest.fixture
def mock_product_is_hidden():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyStockManager._product_is_hidden"
    ) as m:
        yield m


def test_update_out_of_stock_method(mock_get_products, mock_update_product_status):
    products = [mock.Mock() for _ in range(3)]
    mock_get_products.return_value = products
    ShopifyStockManager.update_out_of_stock()
    mock_get_products.assert_called_once_with()
    mock_update_product_status.assert_has_calls(
        mock.call(product) for product in products
    )


def test_update_product_status_method_calls_get_stock_level(
    mock_shopify_manager, mock_get_stock_level, mock_product_is_hidden
):
    product = mock.Mock()
    ShopifyStockManager._update_product_status(product)
    mock_get_stock_level.assert_called_once_with(product)


def test_update_product_status_method_calls_product_is_hidden(
    mock_shopify_manager, mock_get_stock_level, mock_product_is_hidden
):
    product = mock.Mock()
    ShopifyStockManager._update_product_status(product)
    mock_product_is_hidden.assert_called_once_with(product)


def test_update_product_status_method_hides_product(
    mock_shopify_manager, mock_get_stock_level, mock_product_is_hidden
):
    product = mock.Mock()
    mock_get_stock_level.return_value = 0
    mock_product_is_hidden.return_value = False
    ShopifyStockManager._update_product_status(product)
    mock_shopify_manager._hide_product.assert_called_once_with(product)
    mock_shopify_manager._unhide_product.assert_not_called()


def test_update_product_status_method_unhides_product(
    mock_shopify_manager, mock_get_stock_level, mock_product_is_hidden
):
    product = mock.Mock()
    mock_get_stock_level.return_value = 1
    mock_product_is_hidden.return_value = True
    ShopifyStockManager._update_product_status(product)
    mock_shopify_manager._unhide_product.assert_called_once_with(product)
    mock_shopify_manager._hide_product.assert_not_called()


def test_update_product_status_method_with_active_in_stock_product(
    mock_shopify_manager, mock_get_stock_level, mock_product_is_hidden
):
    product = mock.Mock()
    mock_get_stock_level.return_value = 1
    mock_product_is_hidden.return_value = False
    ShopifyStockManager._update_product_status(product)
    mock_shopify_manager._hide_product.assert_not_called()
    mock_shopify_manager._unhide_product.assert_not_called()


def test_update_product_status_method_with_inactive_out_of_stock_product(
    mock_shopify_manager, mock_get_stock_level, mock_product_is_hidden
):
    product = mock.Mock()
    mock_get_stock_level.return_value = 0
    mock_product_is_hidden.return_value = True
    ShopifyStockManager._update_product_status(product)
    mock_shopify_manager._hide_product.assert_not_called()
    mock_shopify_manager._unhide_product.assert_not_called()


def test_get_products_method(mock_shopify_manager):
    value = ShopifyStockManager._get_products()
    mock_shopify_manager._get_products.assert_called_once_with()
    assert value == mock_shopify_manager._get_products.return_value


def test_get_stock_level_method():
    product = mock.Mock(
        variants=[
            mock.Mock(inventory_quantity=3),
            mock.Mock(inventory_quantity=5),
            mock.Mock(inventory_quantity=0),
        ]
    )
    assert ShopifyStockManager._get_stock_level(product) == 8


@pytest.mark.parametrize(
    "status,expected", ((ShopifyManager.ACTIVE, False), (ShopifyManager.DRAFT, True))
)
def test_product_is_hidden_method(status, expected):
    product = mock.Mock(status=status)
    assert ShopifyStockManager._product_is_hidden(product) is expected
