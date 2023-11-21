import datetime as dt
from decimal import Decimal
from unittest import mock

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from home.models import Staff
from purchases import models
from shipping.models import ShippingPrice


@pytest.fixture
def purchased_by(staff_factory):
    return staff_factory.create()


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


@pytest.fixture
def shipping_price(shipping_price_factory, shipping_service, country):
    return shipping_price_factory.create(
        shipping_service=shipping_service, country=country
    )


@pytest.fixture
def quantity():
    return 2


@pytest.fixture
def weight():
    return 500


@pytest.fixture
def purchase(shipping_purchase_factory):
    purchase = shipping_purchase_factory.create()
    return purchase


@pytest.mark.django_db
def test_full_clean(purchase):
    assert purchase.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_purchase_has_purchased_by_attribute(purchase):
    assert isinstance(purchase.purchased_by, Staff)


@pytest.mark.django_db
def test_purchase_has_shipping_service_attribute(purchase):
    assert isinstance(purchase.shipping_service, ShippingPrice)


@pytest.mark.django_db
def test_purchase_has_quantity_attribute(purchase):
    assert isinstance(purchase.quantity, int)


@pytest.mark.django_db
def test_purchase_has_time_of_purchase_price_attribute(purchase):
    assert isinstance(purchase.time_of_purchase_price, Decimal)


@pytest.mark.django_db
def test_purchase_price_has_export_attribute(purchase):
    assert isinstance(purchase.export, models.PurchaseExport)


@pytest.mark.django_db
def test_purchase_price_has_created_at_attribute(purchase):
    assert isinstance(purchase.created_at, dt.datetime)


@pytest.mark.django_db
def test_purchase_price_has_modified_at_attribute(purchase):
    assert isinstance(purchase.modified_at, dt.datetime)


# Test Methods


@pytest.mark.django_db
def test_to_pay_method(purchase):
    purchase.quantity = 2
    purchase.time_of_purchase_price = Decimal("15.22")
    assert purchase.to_pay() == 30.44


@pytest.mark.django_db
def test_description_property(purchase):
    assert purchase.description == purchase.shipping_service.shipping_service.name


@pytest.mark.django_db
def test_item_price_property(purchase):
    purchase.time_of_purchase_price = Decimal("5.22")
    assert purchase.item_price == 5.22


@pytest.mark.django_db
def test_str_method(shipping_purchase_factory):
    purchase = shipping_purchase_factory.create(
        shipping_service__shipping_service__name="RM24",
        purchased_by__first_name="Joe",
        purchased_by__second_name="Man",
        quantity=2,
    )
    assert str(purchase) == "2 X RM24 for Joe Man"


@pytest.mark.django_db
def test_get_absolute_url_method(purchase):
    assert purchase.get_absolute_url() == reverse(
        "purchases:update_shipping_purchase", args=[purchase.pk]
    )


# Test Manager


@pytest.fixture
def new_purchase(
    shipping_price, purchased_by, shipping_service, quantity, weight, country
):
    return models.ShippingPurchase.objects.new_purchase(
        weight=weight,
        purchased_by=purchased_by,
        shipping_service=shipping_service,
        country=country,
        quantity=quantity,
    )


@pytest.mark.django_db
def test_new_purchase_sets_purchased_by(new_purchase, purchased_by):
    assert new_purchase.purchased_by == purchased_by


@pytest.mark.django_db
def test_new_purchase_sets_shipping_service(new_purchase, shipping_price):
    assert new_purchase.shipping_service == shipping_price


@pytest.mark.django_db
def test_new_purchase_sets_quantity(new_purchase, quantity):
    assert new_purchase.quantity == quantity


@pytest.mark.django_db
@mock.patch("purchases.models.ShippingPurchaseManager._calculate_shipping")
def test_new_purchase_sets_time_of_purchase_price(
    mock_calculate_shipping,
    shipping_price,
    weight,
    purchased_by,
    shipping_service,
    country,
    quantity,
):
    mock_calculate_shipping.return_value = 412
    new_purchase = models.ShippingPurchase.objects.new_purchase(
        weight=weight,
        purchased_by=purchased_by,
        shipping_service=shipping_service,
        country=country,
        quantity=quantity,
    )
    mock_calculate_shipping.assert_called_once_with(
        shipping_price=shipping_price, weight=weight
    )
    assert new_purchase.time_of_purchase_price == mock_calculate_shipping.return_value


@pytest.mark.django_db
def test_new_purchase_sets_weight_grams(new_purchase, weight):
    assert new_purchase.weight_grams == weight


@pytest.mark.django_db
def test_new_purchase_does_not_set_export(new_purchase):
    assert new_purchase.export is None


@pytest.mark.django_db
def test_cannot_create_product_purchase_with_zero_quantity(
    purchased_by, shipping_price, shipping_service, weight, country
):
    with pytest.raises(ValidationError):
        models.ShippingPurchase.objects.new_purchase(
            purchased_by=purchased_by,
            shipping_service=shipping_service,
            quantity=0,
            weight=weight,
            country=country,
        )


@mock.patch("purchases.models.ShippingPrice")
def test_get_shipping_price_method(mock_shipping_price):
    country = mock.Mock()
    shipping_service = mock.Mock()
    value = models.ShippingPurchaseManager._get_shipping_price(
        shipping_service=shipping_service, country=country
    )
    mock_shipping_price.objects.find_shipping_price.assert_called_once_with(
        country=country, shipping_service=shipping_service
    )
    assert value == mock_shipping_price.objects.find_shipping_price.return_value


def test_calculate_shipping_method(weight):
    shipping_price = mock.Mock()
    shipping_price.price.return_value = 4225
    value = models.ShippingPurchaseManager._calculate_shipping(shipping_price, weight)
    shipping_price.price.assert_called_once_with(weight)
    assert value == Decimal("42.25")
