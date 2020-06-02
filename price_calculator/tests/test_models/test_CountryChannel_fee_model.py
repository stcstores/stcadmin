import pytest

from price_calculator import models


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def min_channel_fee():
    return 10


@pytest.fixture
def new_country_channel_fee(country, min_channel_fee):
    fee = models.CountryChannelFee(country=country, min_channel_fee=min_channel_fee)
    fee.save()
    return fee


@pytest.mark.django_db
def test_sets_country(new_country_channel_fee, country):
    assert new_country_channel_fee.country == country


@pytest.mark.django_db
def test_sets_min_channel_fee(new_country_channel_fee, min_channel_fee):
    assert new_country_channel_fee.min_channel_fee == min_channel_fee
