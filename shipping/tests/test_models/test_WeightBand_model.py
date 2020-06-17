import pytest

from shipping import models


@pytest.fixture
def shipping_price(shipping_price_factory):
    return shipping_price_factory.create(item_price=0, price_per_kg=0)


@pytest.fixture
def min_weight():
    return 1000


@pytest.fixture
def max_weight():
    return 2000


@pytest.fixture
def price():
    return 950


@pytest.fixture
def new_weight_band(shipping_price, min_weight, max_weight, price):
    weight_band = models.WeightBand(
        shipping_price=shipping_price,
        min_weight=min_weight,
        max_weight=max_weight,
        price=price,
    )
    weight_band.save()
    return weight_band


@pytest.mark.django_db
def test_sets_shipping_price(new_weight_band, shipping_price):
    assert new_weight_band.shipping_price == shipping_price


@pytest.mark.django_db
def test_sets_min_weight(new_weight_band, min_weight):
    assert new_weight_band.min_weight == min_weight


@pytest.mark.django_db
def test_sets_max_weight(new_weight_band, max_weight):
    assert new_weight_band.max_weight == max_weight


@pytest.mark.django_db
def test_sets_price(new_weight_band, price):
    assert new_weight_band.price == price


@pytest.mark.django_db
def test__str__method(weight_band_factory):
    weight_band = weight_band_factory.build()
    assert str(weight_band) == (
        f"{weight_band.shipping_price} {weight_band.min_weight}g -"
        f" {weight_band.max_weight}g"
    )
