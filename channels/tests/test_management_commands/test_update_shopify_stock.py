from unittest import mock

import pytest

from channels.management import commands


@pytest.fixture
def mock_shopify_stock_manager():
    with mock.patch(
        "channels.management.commands.update_shopify_stock.ShopifyStockManager"
    ) as m:
        yield m


@pytest.fixture
def mock_logger():
    with mock.patch("channels.management.commands.update_shopify_stock.logger") as m:
        yield m


def test_update_shopify_collection_command(mock_logger, mock_shopify_stock_manager):
    commands.update_shopify_stock.Command().handle()
    mock_shopify_stock_manager.update_out_of_stock.assert_called_once_with()
    mock_logger.exception.assert_not_called()


def test_update_shopify_collection_command_handles_error(
    mock_logger, mock_shopify_stock_manager
):
    mock_shopify_stock_manager.update_out_of_stock.side_effect = Exception()
    with pytest.raises(Exception):
        commands.update_shopify_stock.Command().handle()
    mock_shopify_stock_manager.update_out_of_stock.assert_called_once_with()
    mock_logger.exception.assert_called_once_with("Error updating shopify stock.")
