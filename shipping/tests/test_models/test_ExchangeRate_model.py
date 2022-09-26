import datetime as dt
from decimal import Decimal

import pytest
from django.db import IntegrityError

from shipping import models


@pytest.fixture
def currency(currency_factory):
    return currency_factory.create()


@pytest.fixture
def date():
    return dt.date(2022, 2, 3)


@pytest.fixture
def rate():
    return "0.962"


@pytest.fixture
def new_exchange_rate(currency, date, rate):
    rate = models.ExchangeRate(currency=currency, date=date, rate=rate)
    rate.save()
    return models.ExchangeRate.objects.get(id=rate.id)


@pytest.mark.django_db
def test_has_currency(new_exchange_rate, currency):
    assert new_exchange_rate.currency == currency


@pytest.mark.django_db
def test_has_date(new_exchange_rate, date):
    assert new_exchange_rate.date == date


@pytest.mark.django_db
def test_has_rate(new_exchange_rate, rate):
    assert new_exchange_rate.rate == Decimal(rate)


@pytest.mark.django_db
def test_latest(exchange_rate_factory, date):
    rates = [
        exchange_rate_factory.create(date=date),
        exchange_rate_factory.create(date=date + dt.timedelta(days=1)),
    ]
    assert models.ExchangeRate.objects.latest() == rates[1]


@pytest.mark.django_db
def test_currency_and_date_unique_together(currency, date):
    models.ExchangeRate(currency=currency, date=date, rate=Decimal("0.235")).save()
    with pytest.raises(IntegrityError):
        models.ExchangeRate(currency=currency, date=date, rate=Decimal("0.461")).save()
