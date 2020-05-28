import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test Destination Country"


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def min_channel_fee():
    return 12


@pytest.fixture
def new_destination_country(name, country, min_channel_fee):
    destination_country = models.DestinationCountry(name=name, country=country)
    destination_country.save()
    return destination_country


@pytest.mark.django_db
def test_sets_name(new_destination_country, name):
    assert new_destination_country.name == name


@pytest.mark.django_db
def test_sets_country(new_destination_country, country):
    assert new_destination_country.country == country


@pytest.mark.django_db
def test_sets_min_channel_fee(new_destination_country):
    assert new_destination_country.min_channel_fee is None


@pytest.mark.django_db
def test_can_set_min_chanel_fee(name, country, min_channel_fee):
    destination_country = models.DestinationCountry(
        name=name, country=country, min_channel_fee=min_channel_fee
    )
    destination_country.save()
    assert destination_country.min_channel_fee == min_channel_fee


@pytest.mark.django_db
def test_sets_sort_order(new_destination_country):
    assert new_destination_country.sort_order == 0


@pytest.mark.django_db
def test__str__method(new_destination_country, name):
    assert str(new_destination_country) == name


@pytest.mark.django_db
def test_currency_code_property(destination_country_factory):
    destination_country = destination_country_factory.create()
    assert (
        destination_country.currency_code == destination_country.country.currency.code
    )


@pytest.mark.django_db
def test_currency_symbol_property(destination_country_factory):
    destination_country = destination_country_factory.create()
    assert (
        destination_country.currency_symbol
        == destination_country.country.currency.symbol
    )


@pytest.mark.django_db
def test_exchange_rate_property(destination_country_factory):
    destination_country = destination_country_factory.create()
    assert (
        destination_country.exchange_rate
        == destination_country.country.currency.exchange_rate
    )


def test_no_shipping_service_exception():
    with pytest.raises(models.DestinationCountry.NoShippingService):
        raise models.DestinationCountry.NoShippingService
