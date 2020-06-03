import pytest

from price_calculator import models


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def product_type():
    return models.ProductType.objects.create()


@pytest.mark.django_db
def test_match_shipping_methods_method(country, product_type, shipping_method_factory):
    shipping_method = shipping_method_factory.create(
        country=country, min_weight=250, max_weight=500, min_price=1000, max_price=8000
    )
    shipping_method.product_type.set([product_type])
    returned = models.ShippingMethod.objects.match_shipping_methods(
        country=country, product_type=product_type, weight=300, price=1500
    )
    assert list(returned) == [shipping_method]


@pytest.mark.django_db
def test_get_shipping_price_returns_method_and_price(
    country, product_type, shipping_method_factory, shipping_price_factory
):
    weight = 350
    shipping_method = shipping_method_factory.create(
        country=country, min_weight=250, max_weight=500, min_price=1000, max_price=8000
    )
    shipping_price = shipping_price_factory.create(
        country=country, shipping_service=shipping_method.shipping_service
    )
    shipping_method.product_type.set([product_type])
    returned = models.ShippingMethod.objects.get_shipping_price(
        country=country, product_type=product_type, weight=weight, price=1500
    )
    assert returned == (shipping_method, shipping_price.price(weight))


@pytest.mark.django_db
def test_get_shipping_price_raises_when_no_shipping_method_is_found(
    country, product_type
):
    with pytest.raises(models.NoShippingService):
        models.ShippingMethod.objects.get_shipping_price(
            country=country, product_type=product_type, weight=500, price=1500
        )


@pytest.mark.django_db
def test_get_shipping_price_raises_when_no_shipping_price_is_found(
    country, product_type, shipping_method_factory
):
    shipping_method = shipping_method_factory.create(
        country=country, min_weight=250, max_weight=500, min_price=1000, max_price=8000
    )
    shipping_method.product_type.set([product_type])
    with pytest.raises(models.NoShippingService):
        models.ShippingMethod.objects.get_shipping_price(
            country=country, product_type=product_type, weight=350, price=1500
        )