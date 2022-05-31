import pytest

from shipping import models


@pytest.fixture
def name():
    return "Test Country"


@pytest.fixture
def region(region_factory):
    return region_factory.create()


@pytest.fixture
def currency(currency_factory):
    return currency_factory.create()


@pytest.fixture
def vat_required():
    return models.Country.VAT_NEVER


@pytest.fixture
def default_vat_rate():
    return 17.5


@pytest.fixture
def new_country(name, region, currency):
    country = models.Country(name=name, region=region, currency=currency)
    country.save()
    return country


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
def test_vat_required_defaults_as_region(new_country):
    assert new_country.vat_required == models.Country.VAT_FROM_REGION


@pytest.mark.django_db
def test_default_vat_rate_defaults_to_null(new_country):
    assert new_country.default_vat_rate is None


@pytest.mark.django_db
def test_can_set_vat_required(name, region, currency, vat_required):
    country = models.Country(
        name=name,
        region=region,
        currency=currency,
        vat_required=vat_required,
    )
    country.save()
    country.refresh_from_db()
    assert country.vat_required == vat_required


@pytest.mark.django_db
def test_can_set_default_vat_rate(name, region, currency, default_vat_rate):
    country = models.Country(
        name=name,
        region=region,
        currency=currency,
        default_vat_rate=default_vat_rate,
    )
    country.save()
    country.refresh_from_db()
    assert country.default_vat_rate == default_vat_rate


@pytest.mark.django_db
def test_str_method(country_factory):
    country = country_factory.create()
    assert str(country) == country.name


@pytest.mark.django_db
def test_vat_is_required_method_returns_region_value_as_region(country_factory):
    country = country_factory.create(
        vat_required=models.Country.VAT_FROM_REGION,
        region__vat_required=models.Region.VAT_ALWAYS,
    )
    assert country.vat_is_required() == models.Region.VAT_ALWAYS


@pytest.mark.django_db
def test_vat_is_required_method_returns_vat_required_when_not_none(
    country_factory, vat_required
):
    country = country_factory.create(
        vat_required=vat_required, region__vat_required=models.Region.VAT_VARIABLE
    )
    assert country.vat_is_required() == vat_required


@pytest.mark.django_db
def test_vat_rate_method_returns_region_value_if_none(country_factory):
    country = country_factory.create(default_vat_rate=None, region__default_vat_rate=23)
    assert country.vat_rate() == 23


@pytest.mark.django_db
def test_vat_rate_method_returns_defualt_vat_rate_if_not_none(country_factory):
    country = country_factory.create(default_vat_rate=52, region__default_vat_rate=23)
    assert country.vat_rate() == 52
