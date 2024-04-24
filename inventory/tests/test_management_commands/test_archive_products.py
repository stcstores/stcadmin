from unittest.mock import patch

from inventory.management import commands


@patch("inventory.management.commands.archive_products.Archiver")
def test_archive_products(mock_archiver):
    commands.archive_products.Command().handle()
    mock_archiver.archive_products.assert_called_once_with()
