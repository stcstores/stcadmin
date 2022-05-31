from unittest.mock import patch

import pytest

from shipping.management import commands


@pytest.fixture
def mock_currency():
    with patch(
        "shipping.management.commands.update_exchange_rates.Currency"
    ) as mock_currency:
        yield mock_currency


@pytest.mark.django_db
def test_update(mock_currency):
    commands.update_exchange_rates.Command().handle()
    mock_currency.objects.update_rates.assert_called_once()
    assert len(mock_currency.mock_calls) == 1


@pytest.mark.django_db
def test_error(mock_currency):
    mock_currency.objects.update_rates.side_effect = Exception()
    with pytest.raises(Exception):
        commands.update_exchange_rates.Command().handle()
    mock_currency.objects.update_rates.assert_called_once()
    assert len(mock_currency.mock_calls) == 1
