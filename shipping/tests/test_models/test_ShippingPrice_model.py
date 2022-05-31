import pytest
from django.db import IntegrityError

from shipping import models


@pytest.fixture
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def region(region_factory):
    return region_factory.create()


@pytest.fixture
def new_shipping_price(shipping_service, country):
    shipping_price = models.ShippingPrice(
        shipping_service=shipping_service, country=country
    )
    shipping_price.save()
    return shipping_price


@pytest.mark.django_db
def test_sets_shipping_service(new_shipping_price, shipping_service):
    assert new_shipping_price.shipping_service == shipping_service


@pytest.mark.django_db
def test_sets_country(new_shipping_price, country):
    assert new_shipping_price.country == country


@pytest.fixture
def test_sets_region(new_shipping_price):
    assert new_shipping_price.region is None


@pytest.mark.django_db
def test_sets_item_price(new_shipping_price):
    assert new_shipping_price.item_price == 0


@pytest.mark.django_db
def test_sets_price_per_kg(new_shipping_price):
    assert new_shipping_price.price_per_kg == 0


@pytest.mark.django_db
def test_sets_price_per_g(new_shipping_price):
    assert new_shipping_price.price_per_g == 0


@pytest.mark.django_db
def test_sets_item_surcharge(new_shipping_price):
    assert new_shipping_price.item_surcharge == 0


@pytest.mark.django_db
def test_sets_fuel_surcharge(new_shipping_price):
    assert new_shipping_price.fuel_surcharge == 0


@pytest.mark.django_db
def test_sets_covid_surcharge(new_shipping_price):
    assert new_shipping_price.covid_surcharge == 0


@pytest.mark.django_db
def test_sets_active(new_shipping_price):
    assert new_shipping_price.active is False


@pytest.mark.django_db
def test_can_create_with_region(shipping_service, region):
    shipping_price = models.ShippingPrice(
        shipping_service=shipping_service, region=region
    )
    shipping_price.save()
    assert shipping_price.region == region


@pytest.mark.django_db
def test__str__method_with_country(shipping_price_factory, country):
    shipping_price = shipping_price_factory.create(country=country, region=None)
    assert (
        str(shipping_price)
        == f"{shipping_price.shipping_service} - {shipping_price.country}"
    )


@pytest.mark.django_db
def test__str__method_with_region(shipping_price_factory, region):
    shipping_price = shipping_price_factory.create(country=None, region=region)
    assert str(shipping_price) == f"{shipping_price.shipping_service} - {region}"


@pytest.mark.django_db
def test_fixed_price(shipping_price_factory):
    price = 560
    shipping_price = shipping_price_factory.create(item_price=price, price_per_kg=0)
    assert shipping_price.price(970) == price


@pytest.mark.django_db
def test_kg_price(shipping_price_factory):
    shipping_price = shipping_price_factory.create(item_price=120, price_per_kg=80)
    assert shipping_price.price(1500) == 280


@pytest.mark.django_db
def test_g_price(shipping_price_factory):
    shipping_price = shipping_price_factory.create(
        item_price=120, price_per_kg=0, price_per_g=0.08
    )
    assert shipping_price.price(1500) == 240


@pytest.mark.django_db
def test_weight_band_price(shipping_price_factory, weight_band_factory):
    shipping_price = shipping_price_factory.create(item_price=0, price_per_kg=0)
    weight_band_factory.create(
        min_weight=0, max_weight=200, price=220, shipping_price=shipping_price
    )
    correct_weight_band = weight_band_factory.create(
        min_weight=201, max_weight=500, price=530, shipping_price=shipping_price
    )
    weight_band_factory.create(
        min_weight=501, max_weight=700, price=780, shipping_price=shipping_price
    )
    assert shipping_price.price(350) == correct_weight_band.price


@pytest.mark.django_db
def test_weight_band_with_kg_price(shipping_price_factory, weight_band_factory):
    shipping_price = shipping_price_factory.create(item_price=0, price_per_kg=80)
    weight_band_factory.create(
        min_weight=100, max_weight=2000, price=220, shipping_price=shipping_price
    )
    assert shipping_price.price(1500) == 380


@pytest.mark.django_db
def test_weight_band_with_g_price(shipping_price_factory, weight_band_factory):
    shipping_price = shipping_price_factory.create(
        item_price=0, price_per_kg=0, price_per_g=0.08
    )
    weight_band_factory.create(
        min_weight=100, max_weight=2000, price=220, shipping_price=shipping_price
    )
    assert shipping_price.price(1500) == 340


@pytest.mark.django_db
def test_item_surcharge(shipping_price_factory):
    shipping_price = shipping_price_factory.create(item_price=600, item_surcharge=70)
    assert shipping_price.price(1500) == 670


@pytest.mark.django_db
def test_fuel_surcharge(shipping_price_factory):
    shipping_price = shipping_price_factory.create(item_price=600, fuel_surcharge=10)
    assert shipping_price.price(1500) == 660


@pytest.mark.django_db
def test_covid_surcharge(shipping_price_factory):
    shipping_price = shipping_price_factory.create(item_price=600, covid_surcharge=70)
    assert shipping_price.price(1500) == 670


@pytest.mark.django_db
def test_surcharges(shipping_price_factory):
    shipping_price = shipping_price_factory.create(
        item_price=600, item_surcharge=70, fuel_surcharge=10, covid_surcharge=70
    )
    assert shipping_price.price(1500) == 800


@pytest.mark.django_db
def test_shipping_service_and_country_are_unique_together(
    shipping_service, country, shipping_price_factory
):
    shipping_price_factory.create(shipping_service=shipping_service, country=country)
    with pytest.raises(IntegrityError):
        shipping_price_factory.create(
            shipping_service=shipping_service, country=country
        )


@pytest.mark.django_db
def test_shipping_service_and_region_are_unique_together(
    region, shipping_service, country, shipping_price_factory
):
    shipping_price_factory.create(
        shipping_service=shipping_service, country=None, region=region
    )
    with pytest.raises(IntegrityError):
        shipping_price_factory.create(
            shipping_service=shipping_service, country=None, region=region
        )


@pytest.mark.django_db
def test_shipping_service_cannot_have_both_country_and_region(
    shipping_price_factory, country, region
):
    with pytest.raises(IntegrityError):
        shipping_price_factory.create(country=country, region=region)


@pytest.mark.django_db
def test_country_and_region_cannot_both_be_null(shipping_price_factory):
    with pytest.raises(IntegrityError):
        shipping_price_factory.create(country=None, region=None)


@pytest.mark.django_db
def test_find_shipping_price(
    shipping_price_factory, country_factory, shipping_service_factory
):
    shipping_service = shipping_service_factory.create()
    country = country_factory.create()
    price = shipping_price_factory.create(
        shipping_service=shipping_service, country=country, region=None
    )
    returned = models.ShippingPrice.objects.find_shipping_price(
        country=country, shipping_service=shipping_service
    )
    assert returned == price


@pytest.mark.django_db
def test_find_shipping_price_by_region(
    shipping_price_factory, country_factory, shipping_service_factory
):
    shipping_service = shipping_service_factory.create()
    country = country_factory.create()
    price = shipping_price_factory.create(
        shipping_service=shipping_service, country=None, region=country.region
    )
    returned = models.ShippingPrice.objects.find_shipping_price(
        country=country, shipping_service=shipping_service
    )
    assert returned == price


@pytest.mark.django_db
def test_find_shipping_price_without_match(shipping_service_factory, country_factory):
    shipping_service = shipping_service_factory.create()
    country = country_factory.create()
    with pytest.raises(models.ShippingPrice.DoesNotExist):
        models.ShippingPrice.objects.find_shipping_price(
            country=country, shipping_service=shipping_service
        )
