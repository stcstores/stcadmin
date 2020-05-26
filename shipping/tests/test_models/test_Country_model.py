import pytest

from shipping import models


@pytest.fixture
def country_ID():
    return "839"


@pytest.fixture
def name():
    return "Test Country"


@pytest.fixture
def region():
    return models.Country.EU


@pytest.fixture
def currency(currency_factory):
    return currency_factory.create()


@pytest.fixture
def new_country(country_ID, name, region, currency):
    country = models.Country(
        country_ID=country_ID, name=name, region=region, currency=currency
    )
    country.save()
    return country


@pytest.mark.django_db
def test_country_ID_is_set(country_ID, new_country):
    assert new_country.country_ID == country_ID


@pytest.mark.django_db
def test_name_is_set(name, new_country):
    assert new_country.name == name


@pytest.mark.django_db
def test_region_is_set(region, new_country):
    assert new_country.region == region


@pytest.mark.django_db
def test_currency_is_set(currency, new_country):
    assert new_country.currency == currency


@pytest.mark.django_db
def test_str_method(country_factory):
    country = country_factory.create()
    assert str(country) == country.name
