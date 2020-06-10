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
def price_type():
    return models.ShippingPrice.FIXED


@pytest.fixture
def new_shipping_price(shipping_service, country, price_type):
    shipping_price = models.ShippingPrice(
        shipping_service=shipping_service, country=country, price_type=price_type,
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
def test_sets_price_type(new_shipping_price, price_type):
    assert new_shipping_price.price_type == price_type


@pytest.mark.django_db
def test_sets_item_price(new_shipping_price):
    assert new_shipping_price.item_price == 0


@pytest.mark.django_db
def test_sets_price_per_kg(new_shipping_price):
    assert new_shipping_price.price_per_kg == 0


@pytest.mark.django_db
def test_sets_inactive(new_shipping_price):
    assert new_shipping_price.inactive is False


@pytest.mark.django_db
def test_can_create_with_region(shipping_service, region, price_type):
    shipping_price = models.ShippingPrice(
        shipping_service=shipping_service, region=region, price_type=price_type,
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
    shipping_price = shipping_price_factory.create(
        price_type=models.ShippingPrice.FIXED, item_price=price
    )
    assert shipping_price.price(970) == price


@pytest.mark.django_db
def test_weight_price(shipping_price_factory):
    shipping_price = shipping_price_factory.create(
        price_type=models.ShippingPrice.WEIGHT, item_price=120, price_per_kg=80
    )
    assert shipping_price.price(1500) == 280


@pytest.mark.django_db
def test_weight_band_price(shipping_price_factory, weight_band_factory):
    shipping_price = shipping_price_factory.create(
        price_type=models.ShippingPrice.WEIGHT_BAND
    )
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
def test_price_with_invalid_price_type(shipping_price_factory):
    shipping_price = shipping_price_factory.build()
    shipping_price.price_type = "invalid_price_type"
    with pytest.raises(NotImplementedError):
        shipping_price.price(73)


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
