from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from shipping import models


@pytest.fixture
def name():
    return "Test Country Dollars"


@pytest.fixture
def code():
    return "TCD"


@pytest.fixture
def exchange_rate():
    return 1.275


@pytest.fixture
def new_currency(name, code, exchange_rate):
    currency = models.Currency(name=name, code=code, exchange_rate=exchange_rate)
    currency.save()
    return currency


@pytest.fixture
def mock_rates(currency_factory):
    currencies = [currency_factory.create(exchange_rate=3.45) for _ in range(5)]
    return {currency.code: 1.965 for currency in currencies}


@pytest.fixture
def mock_exchange_rate_response(mock_rates):
    response = MagicMock()
    response.json.return_value = {"rates": mock_rates}
    return response


@pytest.fixture
def mock_exchange_rate_request(mock_exchange_rate_response):
    with patch("shipping.models.requests.get") as mock_get:
        mock_get.return_value = mock_exchange_rate_response
        yield mock_get


@pytest.mark.django_db
def test_currency_name_is_set(name, new_currency):
    assert new_currency.name == name


@pytest.mark.django_db
def test_currency_code_is_set(code, new_currency):
    assert new_currency.code == code


@pytest.mark.django_db
def test_currency_exchange_rate_is_set(exchange_rate, new_currency):
    assert new_currency.exchange_rate == Decimal(exchange_rate)


@pytest.mark.django_db
def test_update_requests_exchange_rates(mock_exchange_rate_request):
    models.Currency.objects.update_rates()
    mock_exchange_rate_request.assert_called_once_with(
        models.Currency.EXCHANGE_RATE_URL
    )


@pytest.mark.django_db()
def test_exchange_rate_update_request_raises_for_status(
    mock_exchange_rate_request, mock_exchange_rate_response
):
    models.Currency.objects.update_rates()
    mock_exchange_rate_response.raise_for_status.assert_called_once()


@pytest.mark.django_db
def test_update(mock_exchange_rate_request, mock_rates):
    models.Currency.objects.update_rates()
    for currency in models.Currency.objects.all():
        expected = str(round(1 / mock_rates[currency.code], 3))
        assert currency.exchange_rate == Decimal(expected)


@pytest.mark.django_db
def test_str_method(currency_factory):
    currency = currency_factory.create()
    assert str(currency) == currency.name
