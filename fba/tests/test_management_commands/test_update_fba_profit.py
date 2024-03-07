from unittest import mock

import pytest

from fba.management import commands


@pytest.fixture
def mock_fba_profit_file_model():
    with mock.patch("fba.management.commands.update_fba_profit.FBAProfitFile") as m:
        yield m


@pytest.fixture
def mock_logger():
    with mock.patch("fba.management.commands.update_fba_profit.logger") as m:
        yield m


def test_update_fba_profit(mock_fba_profit_file_model):
    commands.update_fba_profit.Command().handle()
    mock_fba_profit_file_model.objects.update_from_exports.assert_called_once_with()


def test_update_fba_profit_handles_error(mock_fba_profit_file_model, mock_logger):
    mock_fba_profit_file_model.objects.update_from_exports.side_effect = Exception
    with pytest.raises(Exception):
        commands.update_fba_profit.Command().handle()
    mock_logger.exception.assert_called_with("Error updating FBA profit.")
